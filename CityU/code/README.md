# 1.使用ide打开源码时，请确保切换路径到/src目录下！
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
内存爆了就把Batch_size缩小一半，慢一点但是不影响精度
## 2.6 log
每个src的输出日志
# 3.命名规则
## 3.1 head:
head:代表Task：
- FT=Fine-Tuning
- PT=Pre-Train
- Ensemble-xxx=按xxx方法集成
- Attention-xxx=按xxx方法做注意力机制
- SA-xxx=按xxx的方法做自注意力
- SS=Single-Source
- MS=Multiple-Source
- Template=编程模版
- terminal=如果用Google Colab，那么把该脚本放入谷歌云盘的Colab Notebook文件下，并按顺序执行
## 3.2 net-source-target
net-source-target代表网络结构、源域和目标域