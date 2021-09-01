import sys
import torch
import numpy
import torchvision # MINST数据集由torchvision提供  
import matplotlib.pyplot as plt
from torch.nn.functional import normalize
log = open('../log/MS-FC=resnet18-cifar10.txt','wt')

"""

    Part.1 数据预处理

"""

# 超参数设置
num_epochs = 30   
num_classes = 10
batch_size = 50  
image_size = 32 
learning_rate = 2  

# 定义图像转换
transform = torchvision.transforms.Compose([
    torchvision.transforms.Resize((224, 224)),  # 重置图片大小
    torchvision.transforms.ToTensor(),  # 将图片转换为Tensor,归一化至[0,1]
])

# 导入数据集，允许从互联网下载数据集以及预向量化
train_dataset = torchvision.datasets.CIFAR10(root='../dataset',train=True,transform=transform,download=True) 
test_dataset = torchvision.datasets.CIFAR10(root='../dataset',train=False,transform=transform,download=True)

# 装载训练集，随机划分训练批次
train_loader = torch.utils.data.DataLoader(dataset=train_dataset,batch_size=batch_size,shuffle=True)
epoch_size1 =  len(train_loader.dataset)
print('shape of train set:',epoch_size1,file=log,flush=True)
print('shape of train set:',epoch_size1,file=sys.stdout)

# 全用于测试
indices = range(len(test_dataset)) 

# 使用测试集的index对验证集和测试集随机采样
sampler_test = torch.utils.data.sampler.SubsetRandomSampler(indices)

# 装载测试集，使用随机采样的原测试集index
test_loader = torch.utils.data.DataLoader(dataset=test_dataset,batch_size=batch_size,sampler = sampler_test)
epoch_size2 =  len(test_loader.dataset)

"""

    Part.2 神经网络结构设计

"""

# 来自imagenet的预训练网络
net_1 = torchvision.models.resnet18(pretrained=True)
net_1.fc = torch.nn.Sequential()

# 来自caltech256的预训练网络
net_2 = torchvision.models.resnet18(pretrained=False)
net_2.fc = torch.nn.Linear(512,257) # 预训练模型fc输出257classes，需要重塑resnet的fc才能导入参数
net_2.load_state_dict(torch.load('../pretrained/resnet18-caltech256-pretrained.pth')) 
net_2.fc = torch.nn.Sequential()

# 来自cifar100的预训练网络
net_3 = torchvision.models.resnet18(pretrained=False)
net_3.fc = torch.nn.Linear(512,100) # 预训练模型fc输出100classes，需要重塑resnet的fc才能导入参数
net_3.load_state_dict(torch.load('../pretrained/resnet18-cifar100-pretrained.pth')) 
net_3.fc = torch.nn.Sequential()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device : "+str(device),file=log,flush=True)
print("device : "+str(device),file=sys.stdout)

# 设计FC
class FC(torch.nn.Module):
    
    def __init__(self): 
        super().__init__() # 初始化module父类
        self.fc = torch.nn.Linear(512*3,num_classes)

    def forward(self, x):
        return self.fc(x)

def accuracy(predictions, labels):
    # 统计正确个数，而非正确率 含有_r或_rate的才是百分数
    pred = torch.max(predictions.data, 1)[1] 
    right_num = pred.eq(labels.data.view_as(pred)).sum() 
    return right_num, len(labels)

"""

    Part.3 提取特征

"""

# 网络初始化与参数记录
net_1 = net_1.to(device)
net_2 = net_2.to(device)
net_3 = net_3.to(device)

net_1.eval()
net_2.eval()
net_3.eval()

feature = torch.zeros(50000,1537)

""" 训练集特征提取 """
with torch.no_grad():   
    # batch迭代
    for batch_id, (data,label) in enumerate(train_loader):

        # 拷贝数据
        data = data.to(device)
        # 计算Loss
        output_1 = normalize(net_1(data),dim=1).to('cpu')
        output_2 = normalize(net_2(data),dim=1).to('cpu')
        output_3 = normalize(net_3(data),dim=1).to('cpu')
        for i in range(batch_size):
            feature[i+batch_id*batch_size,0:512] = output_1[i,:]
            feature[i+batch_id*batch_size,512:1024] = output_2[i,:]
            feature[i+batch_id*batch_size,1024:1536] = output_3[i,:]
            feature[i+batch_id*batch_size,1536] = label[i]
    
        """ 可视化：每间隔100个batch打印一次"""
        if batch_id%100 ==0: 
            checkpoint = 'Epoch [{}/{}]\tBatch [{}/{}]\tSample [{}/{}]'.format(
                1,1,min(batch_id+100,epoch_size1//batch_size),epoch_size1//batch_size ,min((batch_id+100) * batch_size,epoch_size1), epoch_size1)
            print(checkpoint,file=log,flush=True)
            print(checkpoint,file=sys.stdout)
numpy.savetxt("../feature/resnet18-multisource-cifar10-features-train.csv",feature.numpy(),delimiter=',')

# features = torch.from_numpy(numpy.loadtxt("../feature/resnet18-multisource-cifar10-features-train.csv", delimiter=','))
features = feature

X_train = features[:,:-1].type(torch.FloatTensor)
y_train = features[:,-1].type(torch.LongTensor)

# 装载features
features_set = torch.utils.data.TensorDataset(X_train,y_train)
features_loader = torch.utils.data.DataLoader(dataset=features_set,batch_size=batch_size,shuffle=True)

# 训练最后的全链接层
net = FC()
net = net.to(device)
best_model_wts = net.state_dict()

# Loss函数采用交叉熵，优化算法采用随机梯度下降
criterion = torch.nn.CrossEntropyLoss() 
optimizer = torch.optim.SGD(net.parameters(), lr=learning_rate, momentum=0.9)

record_err = [] # 错误记录
best_acc_r = 1 # 记录最佳正确率

""" 训练过程 """
# epoch迭代
for epoch in range(num_epochs):

    #记录准确率
    train_accuracy = [] 
    
    # batch迭代
    for batch_id, (data,label) in enumerate(features_loader):

        # 拷贝数据
        data = data.to(device)
        label = label.to(device)

        # 模型训练
        net.train()
        
        # 计算Loss
        output =  net(data) 
        loss = criterion(output, label) 
        
        # 优化权重
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # 计算精度
        accuracies = accuracy(output, label)
        train_accuracy.append(accuracies)
        
        """ 可视化：每间隔100个batch打印一次精度信息"""
        if batch_id%100 ==0: 
                
            # 记录训练集中分类正确样本数与总样本数
            train_r = (sum([tup[0] for tup in train_accuracy]), sum([tup[1] for tup in train_accuracy]))
           
            # 打印准确率：本训练周期Epoch开始后到目前batch的正确率的平均值
            train_acc_r = 100. * train_r[0] / train_r[1]
            checkpoint = 'Epoch [{}/{}]\tBatch [{}/{}]\tSample [{}/{}]\tLoss: {:.6f}\tTrainAccuracy: {:.2f}%'.format(
                epoch+1,num_epochs,min(batch_id+100,epoch_size1//batch_size),epoch_size1//batch_size ,min((batch_id+100) * batch_size,epoch_size1), epoch_size1,
                loss.item(), 
                train_acc_r)
            print(checkpoint,file=log,flush=True)
            print(checkpoint,file=sys.stdout)

"""

    Part.4 精度测试

"""

""" 测试集特征提取 """

feature=torch.zeros(10000,1537)

with torch.no_grad():
    # batch迭代
    for batch_id, (data,label) in enumerate(test_loader):

        # 拷贝数据
        data = data.to(device)
        # 计算Loss
        output_1 = normalize(net_1(data),dim=1).to('cpu')
        output_2 = normalize(net_2(data),dim=1).to('cpu')
        output_3 = normalize(net_3(data),dim=1).to('cpu')
        for i in range(batch_size):
            feature[i+batch_id*batch_size,0:512] = output_1[i,:]
            feature[i+batch_id*batch_size,512:1024] = output_2[i,:]
            feature[i+batch_id*batch_size,1024:1536] = output_3[i,:]
            feature[i+batch_id*batch_size,1536] = label[i]
    
        """ 可视化：每间隔100个batch打印一次"""
        if batch_id%100 ==0: 
            checkpoint = 'Epoch [{}/{}]\tBatch [{}/{}]\tSample [{}/{}]'.format(
                1,1,min(batch_id+100,epoch_size2//batch_size),epoch_size2//batch_size ,min((batch_id+100) * batch_size,epoch_size2), epoch_size2)
            print(checkpoint,file=log,flush=True)
            print(checkpoint,file=sys.stdout)
numpy.savetxt("../feature/resnet18-multisource-cifar10-features-test.csv",feature.numpy(),delimiter=',')

# features = torch.from_numpy(numpy.loadtxt("../feature/resnet18-multisource-cifar10-features-test.csv", delimiter=','))
features = feature
X_test = features[:,:-1].type(torch.FloatTensor)
y_test = features[:,-1].type(torch.LongTensor)

# 装载features
features_set = torch.utils.data.TensorDataset(X_test,y_test)
features_loader = torch.utils.data.DataLoader(dataset=features_set,batch_size=batch_size,shuffle=True)

# 测试最后的全链接层
net.eval() 
test_accuracy = [] # 记录准确率所用列表

with torch.no_grad():
    for data,label in features_loader:
        data = data.to(device)
        label = label.to(device)        
        output = net(data)        
        accuracies = accuracy(output,label)
        test_accuracy.append(accuracies)
        
# 计算准确率
rights = (sum([tup[0] for tup in test_accuracy]), sum([tup[1] for tup in test_accuracy]))
right_rate = 1.0 * rights[0].detach().to('cpu').numpy() / rights[1]

print("TestAccuracy: ",right_rate,file=log,flush=True)
print("TestAccuracy: ",right_rate,file=sys.stdout)