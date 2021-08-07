import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision # MINST数据集由torchvision提供
import torchvision.transforms as transforms  
import matplotlib.pyplot as plt

"""

    Part.1 数据预处理

"""

# 超参数设置
num_epochs = 6   # 训练6代
num_classes = 10 # 分成10类
batch_size = 64  # 每批64个
image_size = 28  # 图像尺寸28*28
learning_rate = 0.001 # 学习率0.001

# 导入数据集，允许从互联网下载数据集以及预向量化
train_dataset = torchvision.datasets.MNIST(root='../dataset',train=True,transform=transforms.ToTensor(),download=True) 
test_dataset = torchvision.datasets.MNIST(root='../dataset',train=False,transform=transforms.ToTensor(),download=True)

# 装载训练集，随机划分训练批次
train_loader = torch.utils.data.DataLoader(dataset=train_dataset,batch_size=batch_size,shuffle=True)
epoch_size =  len(train_loader.dataset)
print('shape of train set:',epoch_size)

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

# CNN结构：5*5卷积层->2*2max池化层->5*5卷积层->2*2max池化层->平铺全连接层->输出全连接层
class ConvNet(nn.Module):
    def __init__(self): # 各层网络结构初始化
        super().__init__() # 初始化module父类
        self.conv1 = nn.Conv2d(1,4,5,padding=2) # 第一类卷积层：1通道输入,4通道输出,5*5卷积核
        self.conv2 = nn.Conv2d(4,8,5,padding=2) # 第二类卷积层：4通道输入,8通道输出,5*5卷积核
        self.fc1 = nn.Linear( 8 * image_size // 4 * image_size // 4 , 512) # 上一层平铺个输入，512个输出
        self.fc2 = nn.Linear(512, num_classes) #512输入，10类数字输出 
        self.pool = nn.MaxPool2d(2, 2) #2*2max池化
        
    def forward(self, x): # 前向传播过程

        # 第一层卷积层，输出层激活函数为ReLU
        x = self.conv1(x)
        x = F.relu(x)  

        #第二层pooling层，图片尺寸变为14*14  
        x = self.pool(x) 

        # 第三层卷积层，输出层激活函数为ReLU
        x = self.conv2(x)      
        x = F.relu(x) 

        # 第四层pooling层，图片尺寸变为7*7
        x = self.pool(x) 

        # 第五层全连接层，输出层激活函数为ReLU
        x = x.view(-1, image_size // 4 * image_size // 4 * 8) # view函数将张量拉平 
        x = self.fc1(x)
        x = F.relu(x) 
        
        # 第六层全连接层，输出层激活函数softmax    
        x = F.dropout(x, training=self.training) # 以0.5概率对此全连接层进行dropout，防止过拟合
        x = self.fc2(x)
        x = F.log_softmax(x,dim=0)     
        
        return x
    
    def retrieve_features(self, x):
        #该函数专门用于提取卷积神经网络的特征图的功能，返回feature_map1, feature_map2为前两层卷积层的特征图
        feature_map1 = F.relu(self.conv1(x)) #完成第一层卷积
        x = self.pool(feature_map1)  # 完成第一层pooling
        #print('type(feature_map1)=',feature_map1)
        #type是一个四维的tensor
        feature_map2 = F.relu(self.conv2(x)) #第二层卷积，两层特征图都存储到了feature_map1, feature_map2中
        return (feature_map1, feature_map2)

def accuracy(predictions, labels):
    # 自定义精度计算函数
    pred = torch.max(predictions.data, 1)[1] 
    right_num = pred.eq(labels.data.view_as(pred)).sum() 
    return right_num, len(labels)

"""

    Part.3 模型训练与训练集/校验集动态评估

"""

# 网络初始化
net = ConvNet() 

# Loss函数采用交叉熵，优化算法采用随机梯度下降
criterion = nn.CrossEntropyLoss() 
optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

record = [] #记录错误率
weights = [] #记录卷积核

""" 训练过程 """
# epoch迭代
for epoch in range(num_epochs):

    #记录准确率
    train_accuracy = [] 
    
    # batch迭代
    for batch_id, (data,target) in enumerate(train_loader):

        # 模型训练
        net.train()
        
        # 计算Loss
        output =  net(data) 
        loss = criterion(output, target) 
        
        # 优化权重
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # 计算精度
        accuracies = accuracy(output, target)
        train_accuracy.append(accuracies)
        
        """ 可视化：每间隔100个batch打印一次精度信息"""
        if batch_id%100 ==0: 

            # 模型评估(训练集、校验集)
            net.eval() 
            val_accuracy = [] #记录校验数据集准确率
            
            #迭代已遍历过的训练集数据：
            for (data, target) in validation_loader: 

                #完成一次前馈，记录输出
                output = net(data) 

                #记录精度计算所需数据，返回(正确样例数，总样本数)
                accuracies = accuracy(output, target) 
                val_accuracy.append(accuracies)
                
            #记录训练集中分类正确样本数与总样本数
            train_r = (sum([tup[0] for tup in train_accuracy]), sum([tup[1] for tup in train_accuracy]))

            #记录校验集中分类正确样本数与总样本数
            val_r = (sum([tup[0] for tup in val_accuracy]), sum([tup[1] for tup in val_accuracy]))
            
            #打印准确率：本训练周期Epoch开始后到目前batch的正确率的平均值
            print('Epoch [{}/{}]\tBatch [{}/{}]\tSample [{}/{}]\tLoss: {:.6f}\tTrainAccuracy: {:.2f}%\tValidationAccuracy: {:.2f}%'.format(
                epoch+1,num_epochs,min(batch_id+100,epoch_size//batch_size),epoch_size//batch_size ,(batch_id+100) * batch_size, epoch_size,
                loss.item(), 
                100. * train_r[0] / train_r[1], 
                100. * val_r[0] / val_r[1]))
            
            #记录准确率与权重
            record.append((100 - 100. * train_r[0] / train_r[1], 100 - 100. * val_r[0] / val_r[1]))
            
            # weights记录了训练周期中所有卷积核的演化过程。net.conv1.weight就提取出了第一层卷积核的权重
            weights.append([net.conv1.weight.data.clone(), net.conv1.bias.data.clone(), 
                            net.conv2.weight.data.clone(), net.conv2.bias.data.clone()])

#绘制训练过程的误差曲线，验证集和测试集上的错误率。
plt.figure(figsize = (10,7))
plt.plot(record)
plt.xlabel('Steps')
plt.ylabel('Error rate')
plt.show()

"""

    Part.4 精度测试与测试集静态模型评估

"""
# 模型评估(测试集)
net.eval() 
vals = [] #记录准确率所用列表

with torch.no_grad():
    for data,target in test_loader:        
        output = net(data)        
        val = accuracy(output,target)
        vals.append(val)
        
#计算准确率
rights = (sum([tup[0] for tup in vals]), sum([tup[1] for tup in vals]))
right_rate = 1.0 * rights[0].detach().numpy() / rights[1]

print("TestAccuracy: ",right_rate)
