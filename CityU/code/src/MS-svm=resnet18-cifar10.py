import sys
import torch
import numpy
import torchvision # MINST数据集由torchvision提供  
import matplotlib.pyplot as plt
from torch.nn.functional import normalize
import joblib
from sklearn import svm
from sklearn.metrics import accuracy_score
log = open('../log/MS-svm=resnet18-cifar10.txt','wt')

"""

    Part.1 数据预处理

"""

# 超参数设置
# num_epochs = 1   
num_classes = 10
batch_size = 50  
image_size = 32 
# learning_rate = 0.005  

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

# features = numpy.loadtxt("../feature/resnet18-multisource-cifar10-features-train.csv", delimiter=',')
features = feature
X_train = features[:,:-1]
y_train = features[:,-1]
clf = svm.SVC(kernel='rbf',verbose=True) # default : C=1, gamma=1/NUM_OF_FEATURES
print("model fitting...",file=log,flush=True)
print("model fitting...",file=sys.stdout)
clf.fit(X_train,y_train)
joblib.dump(clf, "../model/resnet18-multisource-cifar10-model.pkl")
# clf = joblib.load(clf,"../model/resnet18-multisource-cifar10-model.pkl")


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
# features = numpy.loadtxt("../feature/resnet18-multisource-cifar10-features-train.csv", delimiter=',')
features = feature
X_test = features[:,:-1]
y_test = features[:,-1]
y_hat = clf.predict(X_test)
acc = accuracy_score(y_test, y_hat)
print("accuary : " + str(acc),file=log,flush=True)
print("accuary : " + str(acc),file=sys.stdout)