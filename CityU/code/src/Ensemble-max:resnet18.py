import sys
import torch
import torchvision # MINST数据集由torchvision提供  
import matplotlib.pyplot as plt
from torch.nn.functional import normalize
log = open('../log/Ensemble-max:resnet18-log.txt','wt')

"""

    Part.1 数据预处理

"""

# 超参数设置
num_epochs = 5   
num_classes = 10
batch_size = 50  
image_size = 32 
learning_rate = 0.001  

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

# 来自imagenet的预训练网络
net_1 = torchvision.models.resnet18(pretrained=True)
net_1.fc = torch.nn.Linear(512,num_classes)

# 来自caltech256的预训练网络
net_2 = torchvision.models.resnet18(pretrained=False)
net_2.fc = torch.nn.Linear(512,257) # 预训练模型fc输出257classes，需要重塑resnet的fc才能导入参数
net_2.load_state_dict(torch.load('../pretrained/resnet18-caltech256-pretrained.pth')) 
net_2.fc = torch.nn.Linear(512,num_classes)

# 来自cifar100的预训练网络
net_3 = torchvision.models.resnet18(pretrained=False)
net_3.fc = torch.nn.Linear(512,100) # 预训练模型fc输出100classes，需要重塑resnet的fc才能导入参数
net_3.load_state_dict(torch.load('../pretrained/resnet18-cifar100-pretrained.pth')) 
net_3.fc = torch.nn.Linear(512,num_classes)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device : "+str(device),file=log,flush=True)

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
best_model_wts_1 = net_1.state_dict()
best_model_wts_2 = net_2.state_dict()
best_model_wts_3 = net_3.state_dict()

# Loss函数采用交叉熵，优化算法采用随机梯度下降
criterion = torch.nn.CrossEntropyLoss() 
optimizer_1 = torch.optim.SGD(net_1.parameters(), lr=learning_rate, momentum=0.9)
optimizer_2 = torch.optim.SGD(net_2.parameters(), lr=learning_rate, momentum=0.9)
optimizer_3 = torch.optim.SGD(net_3.parameters(), lr=learning_rate, momentum=0.9)

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
            output_cat = torch.zeros(3,num_classes)
            output_cat[0,:] = output_1[i,:]
            output_cat[1,:] = output_2[i,:]
            output_cat[2,:] = output_3[i,:]
            output[i,:] = torch.max(output_cat,dim=0).values 
        loss = criterion(output, label) 
        
        # 优化权重
        optimizer_1.zero_grad()
        optimizer_2.zero_grad()
        optimizer_3.zero_grad()
        loss.backward()
        optimizer_1.step()
        optimizer_2.step()
        optimizer_3.step()
        
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
                    output_cat = torch.zeros(3,num_classes)
                    output_cat[0,:] = output_1[i,:]
                    output_cat[1,:] = output_2[i,:]
                    output_cat[2,:] = output_3[i,:]
                    output[i,:] = torch.max(output_cat,dim=0).values 

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
            print('Epoch [{}/{}]\tBatch [{}/{}]\tSample [{}/{}]\tLoss: {:.6f}\tTrainAccuracy: {:.2f}%\tValidationAccuracy: {:.2f}%'.format(
                epoch+1,num_epochs,min(batch_id+100,epoch_size//batch_size),epoch_size//batch_size ,min((batch_id+100) * batch_size,epoch_size), epoch_size,
                loss.item(), 
                train_acc_r, 
                val_acc_r),file=log,flush=True)
            if(val_acc_r > best_acc_r):
                best_acc_r = val_acc_r
                best_model_wts_1 = net_1.state_dict()
                best_model_wts_2 = net_2.state_dict()
                best_model_wts_3 = net_3.state_dict()
            # 记录错误率
            record_err.append((100 - train_acc_r, 100 - val_acc_r))


# 绘制训练过程的误差曲线，验证集和测试集上的错误率。
plt.figure(figsize = (10,7))
plt.plot(record_err)
plt.xlabel('Steps')
plt.ylabel('Error rate(%)')
plt.show()

# 保存最佳模型参数
torch.save(best_model_wts_1, "../model/ensemble-max-1.pth")
torch.save(best_model_wts_2, "../model/ensemble-max-2.pth")
torch.save(best_model_wts_3, "../model/ensemble-max-3.pth")

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
            output_cat = torch.zeros(3,num_classes)
            output_cat[0,:] = output_1[i,:]
            output_cat[1,:] = output_2[i,:]
            output_cat[2,:] = output_3[i,:]
            output[i,:] = torch.max(output_cat,dim=0).values        
        accuracies = accuracy(output,label)
        test_accuracy.append(accuracies)
        
# 计算准确率
rights = (sum([tup[0] for tup in test_accuracy]), sum([tup[1] for tup in test_accuracy]))
right_rate = 1.0 * rights[0].detach().to('cpu').numpy() / rights[1]

print("TestAccuracy: ",right_rate,file=log,flush=True)