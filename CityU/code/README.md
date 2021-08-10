# 1.使用ide打开源码时，请确保切换路径到/code目录下！
# 2.目录结构：
## 2.1 dataset
一些torchvision上没有的、从互联网上收集来的原始数据集(.gitignore)
## 2.2 feature
由pretrained model提取出来的features，以csv格式存储(.gitignore)
## 2.3 model
代码生成的模型
## 2.4 pretrained
预训练模型，多数来自于互联网，少数是代码生成的
## 2.5 src
源码
# 3.命名规则
## 3.1 head:
head:代表Task：
- FT:Fine-Tuning
- PT:Pre-Train
- SS:Single-Source
- MS:Multiple-Source
- Template:编程模版
## 3.2 net-source-target
net-source-target代表网络结构、源域和目标域