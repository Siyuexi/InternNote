import sys
import torch
from torch.nn import parameter
import torchvision # MINST数据集由torchvision提供  
import matplotlib.pyplot as plt
from torch.nn.functional import normalize
log = open('../log/Attention-transformer=resnet18-log.txt','wt')

"""

    Part.1 数据预处理

"""

# 超参数设置
num_epochs = 10   
num_classes = 10
batch_size = 50  
image_size = 32 
learning_rate = 0.01  

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
epoch_size =  len(train_loader.dataset)
print('shape of train set:',epoch_size,file=log,flush=True)
print('shape of train set:',epoch_size,file=sys.stdout)

# 测试集index前5000的是验证集，index后5000的是测试集
indices = range(len(test_dataset))
indices_val = indices[:5000]
indices_test = indices[5000:]  

# 使用测试集的index对验证集和测试集随机采样
sampler_val = torch.utils.data.sampler.SubsetRandomSampler(indices_val)
sampler_test = torch.utils.data.sampler.SubsetRandomSampler(indices_test)

# 装载验证集，使用随机采样的原测试集index
validation_loader = torch.utils.data.DataLoader(dataset=test_dataset,batch_size = batch_size,sampler = sampler_val)
# 装载测试集，使用随机采样的原测试集index
test_loader = torch.utils.data.DataLoader(dataset=test_dataset,batch_size=batch_size,sampler = sampler_test)

"""

    Part.2 神经网络结构设计

"""

# 设计Attention部分 是基于RNN的self-attention
class Attention(torch.nn.Module):
    
    def __init__(self): 
        super().__init__() # 初始化module父类

        self.x_dim = 512 # 即输入特征x的维度
        self.p_dim = 32 # 参数矩阵的转换维度
        self.key = torch.nn.Linear(self.x_dim,self.p_dim,bias=False) # 映射生成key的层
        self.value = torch.nn.Linear(self.x_dim,self.p_dim,bias=False) # 映射生成value的层
        self.query = torch.nn.Linear(self.x_dim*3,self.p_dim,bias=False) # 映射生成query的层
        self.fc = torch.nn.Linear(self.p_dim,num_classes) # 最终分类的全链接层 由最终注意力输出分类

    def forward(self, x):
        # 输入的x分三个部分
        x_1 = x[0,:].to(device)
        x_2 = x[1,:].to(device)
        x_3 = x[2,:].to(device)

        # 求key
        k_1 = self.key(x_1)
        k_2 = self.key(x_2)
        k_3 = self.key(x_3)

        # 求value
        v_1 = self.value(x_1)
        v_2 = self.value(x_2)
        v_3 = self.value(x_3)

        # 求query
        y = torch.cat((x_1,x_2,x_3)) # 假设目标y是前三者的cat
        q = self.query(y)

        # 求系数a
        a_1 = q.dot(k_1)
        a_2 = q.dot(k_2)
        a_3 = q.dot(k_3)
        a_cat = torch.tensor([a_1,a_2,a_3])
        a_1,a_2,a_3 = torch.softmax(a_cat,dim=0)

        # 求注意力c
        c = a_1*v_1+a_2*v_2+a_3*v_3

        # 分类的全链接层
        output = self.fc(c)

        return output

attention = Attention()

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

def accuracy(predictions, labels):
    # 统计正确个数，而非正确率 含有_r或_rate的才是百分数
    pred = torch.max(predictions.data, 1)[1] 
    right_num = pred.eq(labels.data.view_as(pred)).sum() 
    return right_num, len(labels)

"""

    Part.3 模型训练与训练集/校验集动态评估

"""

# 网络初始化与参数记录
net_1 = net_1.to(device)
net_2 = net_2.to(device)
net_3 = net_3.to(device)
attention = attention.to(device)

best_model_wts_1 = net_1.state_dict()
best_model_wts_2 = net_2.state_dict()
best_model_wts_3 = net_3.state_dict()
best_model_wts_attention = attention.state_dict()

# Loss函数采用交叉熵，优化算法采用随机梯度下降
criterion = torch.nn.CrossEntropyLoss() 
optimizer_1 = torch.optim.SGD(net_1.parameters(), lr=learning_rate, momentum=0.9)
optimizer_2 = torch.optim.SGD(net_2.parameters(), lr=learning_rate, momentum=0.9)
optimizer_3 = torch.optim.SGD(net_3.parameters(), lr=learning_rate, momentum=0.9)
optimizer_attention = torch.optim.SGD(attention.parameters(), lr=learning_rate, momentum=0.9)

record_err = [] # 错误记录
best_acc_r = 1 # 记录最佳正确率

""" 训练过程 """
# epoch迭代
for epoch in range(num_epochs):

    #记录准确率
    train_accuracy = [] 
    
    # batch迭代
    for batch_id, (data,label) in enumerate(train_loader):

        # 拷贝数据
        data = data.to(device)
        label = label.to(device)

        # 模型训练
        net_1.train()
        net_2.train()
        net_3.train()
        
        # 计算Loss
        output_1 = normalize(net_1(data),dim=1)
        output_2 = normalize(net_2(data),dim=1)
        output_3 = normalize(net_3(data),dim=1)
        output = torch.zeros(batch_size,num_classes).to(device)
        for i in range(batch_size):
            output_cat = torch.zeros(3,512)
            output_cat[0,:] = output_1[i,:]
            output_cat[1,:] = output_2[i,:]
            output_cat[2,:] = output_3[i,:]
            output[i,:] = attention(output_cat)
        loss = criterion(output, label) 
        
        # 优化权重
        optimizer_1.zero_grad()
        optimizer_2.zero_grad()
        optimizer_3.zero_grad()
        optimizer_attention.zero_grad()
        loss.backward()
        optimizer_1.step()
        optimizer_2.step()
        optimizer_3.step()
        optimizer_attention.step()
        
        # 计算精度
        accuracies = accuracy(output, label)
        train_accuracy.append(accuracies)
        
        """ 可视化：每间隔100个batch做一次validation，并且打印一次精度信息"""
        if batch_id%100 ==0: 

            # 模型评估(训练集、校验集)
            net_1.eval()
            net_2.eval() 
            net_3.eval()
            val_accuracy = [] #记录校验数据集准确率
            
            #迭代已遍历过的训练集数据：
            for (data, label) in validation_loader: 

                # 拷贝数据
                data = data.to(device)
                label = label.to(device)

                # 完成一次前馈，记录输出
                output_1 = normalize(net_1(data),dim=1)
                output_2 = normalize(net_2(data),dim=1)
                output_3 = normalize(net_3(data),dim=1)
                output = torch.zeros(batch_size,num_classes).to(device)
                for i in range(batch_size):
                    output_cat = torch.zeros(3,512)
                    output_cat[0,:] = output_1[i,:]
                    output_cat[1,:] = output_2[i,:]
                    output_cat[2,:] = output_3[i,:]
                    output[i,:] = attention(output_cat)

                # 记录精度计算所需数据，返回(正确样例数，总样本数)
                accuracies = accuracy(output, label) 
                val_accuracy.append(accuracies)
                
            # 记录训练集中分类正确样本数与总样本数
            train_r = (sum([tup[0] for tup in train_accuracy]), sum([tup[1] for tup in train_accuracy]))

            # 记录校验集中分类正确样本数与总样本数
            val_r = (sum([tup[0] for tup in val_accuracy]), sum([tup[1] for tup in val_accuracy]))
            
            # 打印准确率：本训练周期Epoch开始后到目前batch的正确率的平均值
            train_acc_r = 100. * train_r[0] / train_r[1]
            val_acc_r = 100. * val_r[0] / val_r[1]
            checkpoint = 'Epoch [{}/{}]\tBatch [{}/{}]\tSample [{}/{}]\tLoss: {:.6f}\tTrainAccuracy: {:.2f}%\tValidationAccuracy: {:.2f}%'.format(
                epoch+1,num_epochs,min(batch_id+100,epoch_size//batch_size),epoch_size//batch_size ,min((batch_id+100) * batch_size,epoch_size), epoch_size,
                loss.item(), 
                train_acc_r, 
                val_acc_r)
            print(checkpoint,file=log,flush=True)
            print(checkpoint,file=sys.stdout)
            if(val_acc_r > best_acc_r):
                best_acc_r = val_acc_r
                best_model_wts_1 = net_1.state_dict()
                best_model_wts_2 = net_2.state_dict()
                best_model_wts_3 = net_3.state_dict()
                best_model_wts_attention = attention.state_dict()
            # 记录错误率
            record_err.append((100 - train_acc_r, 100 - val_acc_r))


# 绘制训练过程的误差曲线，验证集和测试集上的错误率。
plt.figure(figsize = (10,7))
plt.plot(record_err)
plt.xlabel('Steps')
plt.ylabel('Error rate(%)')
plt.show()

# 保存最佳模型参数
torch.save(best_model_wts_1, "../model/attention-transformer-1.pth")
torch.save(best_model_wts_2, "../model/attention-transformer-2.pth")
torch.save(best_model_wts_3, "../model/attention-transformer-3.pth")
torch.save(best_model_wts_attention, "../model/attention-transformer-attention.pth")

"""

    Part.4 精度测试与测试集静态模型评估

"""
# 模型评估(测试集)
net_1.eval()
net_2.eval()
net_3.eval() 
test_accuracy = [] # 记录准确率所用列表

with torch.no_grad():
    for data,label in test_loader:
        data = data.to(device)
        label = label.to(device)        
        output_1 = normalize(net_1(data),dim=1)
        output_2 = normalize(net_2(data),dim=1)
        output_3 = normalize(net_3(data),dim=1)
        output = torch.zeros(batch_size,num_classes).to(device)
        for i in range(batch_size):
            output_cat = torch.zeros(3,512)
            output_cat[0,:] = output_1[i,:]
            output_cat[1,:] = output_2[i,:]
            output_cat[2,:] = output_3[i,:]
            output[i,:] = attention(output_cat)     
        accuracies = accuracy(output,label)
        test_accuracy.append(accuracies)
        
# 计算准确率
rights = (sum([tup[0] for tup in test_accuracy]), sum([tup[1] for tup in test_accuracy]))
right_rate = 1.0 * rights[0].detach().to('cpu').numpy() / rights[1]

print("TestAccuracy: ",right_rate,file=log,flush=True)
print("TestAccuracy: ",right_rate,file=sys.stdout)