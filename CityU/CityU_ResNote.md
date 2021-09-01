# CityU_ResNote

2021.05.12-Unknown

Hongkong,China

siyuexi@hust.edu.cn

## Knowledge



### 正交矩阵

即满足$A^TA=I$的矩阵。若矩阵$A=[a_1,a_2,...,a_i]$且$a_i$为各个列向量，则矩阵乘积展开后可以得到如下关系：
$$
a_ia_j=\begin{cases}
1,&i=j\\
0,&i\neq j
\end{cases}
$$
即矩阵内各向量之间相互正交。

对于正交矩阵，组成它的列向量构成了一个空间的基，称之为：规范正交基。 对于一个空间而言，可以找到很多个不同的基来表示的(参考相似矩阵的基底变换)。因此可以找到一组基础变换$P_1P_2...P_n$使得该空间的正交基被变换到各个坐标轴上，此时矩阵为对角矩阵。

可以归纳为：**正交矩阵一定可以转换为对角矩阵**



### 矩阵分解

$A$为$n$阶方阵，若数$λ$和$n$维非0列向量$x$满足
$$
Ax=\lambda x
$$
那么数$λ$称为$A$的特征值，$x$称为$A$的对应于特征值$λ$的特征向量。

式$Ax=λx$也可写成
$$
(A-\lambda E)x=0
$$
并且$|λE-A|$即为$A$ 的特征多项式。当特征多项式等于0的时候，称为$A$的特征方程，特征方程是一个齐次线性方程组，求解特征值的过程其实就是求解特征方程的解。

求解特征多项式=0的方程并得到特征向量、特征值，矩阵$A$可以被分解为以下形式：
$$
A=W\Sigma W^{-1}
$$
其中$W$是特征向量构成的特征矩阵，$\Sigma$是特征值组成的对角矩阵。

把$W$中的向量进行标准化处理，即使得$w_i^tw_i=1$。设矩阵具有不同特征值，即特征向量相互正交（对于鲁棒的图结构表示矩阵而言都是满足的），那么这样便得到了**标准正交化**的一组基$W$。由正交矩阵的定义可得：
$$
A=W\Sigma W^T
$$
这样方阵$A$就完成了**特征值矩阵分解**。特征值矩阵的分解在数据压缩领域有着及其重要的应用。如长宽相等的灰度图像可以直接进行特征值分解，再将$\Sigma$中的特征值排序，去掉较小的一半特征值（置零），再进行反变换，其图像只是稍微变得模糊，肉眼感知上差距不明显。

但是在大多数情况下，矩阵$A$并非是方阵。因此不能进行特征值分解。可以采用另一种思路分解：
$$
A=U\Sigma V^T
$$
这里设$A$是一个$m\times n$大小的矩阵，那么$U$是$m\times m$大小的方阵，$V$是$n\times n$大小的方阵。

由于$AA^T$与$A^TA$分别和$U$，$V$矩阵有相同的维度。由于他们都是方阵，可以认为$U$，$V$即为$AA^T$与$A^TA$的特征向量所构成的矩阵（证明略）。
$$
Uu_i=(AA^T)u_i=\lambda_i u_i\\
Vv_i=(A^TA)v_i=\lambda_i v_i\\
$$
这里把$AA^T$的每个特征向量$u_i$称为$A$的左奇异向量，$A^TA$的每个特征向量$v_i$称为$A$的右奇异向量。

$A$的奇异值矩阵$\Sigma$可以通过下式求得：
$$
A=U\Sigma V^T \Rightarrow AV=U\Sigma \Rightarrow Av_i=\sigma_i u_i \Rightarrow \sigma _i=\frac{A v_i}{u_i}
$$
这就是**奇异值分解**。奇异值分解也广泛适用于数据降维任务，如PCA（主成分分析）中对数据间的协方差矩阵进行降维操作，原理同图像压缩算法一致。



### 图网络模型简述

长期以来，深度学习在CV领域的模型（如CNN）基本都建立在数字图像处理的传统理论之上。其基本的数据降维操作——卷积，本质是模板（卷积核）在**图像（image）**每个像素的**邻域**上进行线性运算的过程。这里的邻域即为矩形图像的欧氏空间邻域。

但扩展到例如小样本学习等场景下时，模型所重视的不再是每个图像本身的信息，而是图像（或者一些其他任务）之间的**关联**。这就意味着每个结点可能不再仅仅与“周围”的结点有关。“关系网络”可能会拥有更加复杂的拓扑结构，而非像图像一样依旧保持着规则的8邻域结构。鉴于小样本学习的结点网络可能存在于非欧空间中，因此使用**图（graph）**会更加实用：图之间的关系高度自定义化，且不规则。图网络使得关系网络错综复杂的事务有了更直观具象化的模型表示。

但是更自定义化的关系也带来了表示和计算的复杂度：

1. 图网络需要由邻接矩阵定义拓扑结构，而图像则不需要。前者意味着更大的空间开销以及更多的读写时间开销。
2. 原先定义在二维图像上的卷积操作具有严格的数学意义，并且易于计算。然而卷积操作在图上变得难以实现，需要基于邻接矩阵的分解来计算，并且不再具有和一维连续函数的卷积运算严格相同的数学意义。



### 图网络模型的基本计算

GCN（默认为无向图）的拓扑结构常常被表示为**正则化拉普拉斯矩阵**而非一般性的邻接矩阵。这样能带来更多的信息（如度矩阵），并且易于计算（正交化）：
$$
L=I_n-D^{-\frac{1}{2}}AD^{-\frac{1}{2}}
$$
其中，$A$为邻接矩阵，$D$为度矩阵

正则化拉普拉斯矩阵具有半正定性质，因此可以进行矩阵分解：
$$
L=U\Lambda U^{-1}=U\Lambda U^T
$$
其中$U$是**标准正交化**的特征矩阵，由标准正交化的特征向量组成。标准正交化使得矩阵$U$的逆即为其转置，减少了计算开销；$\Lambda$即与$U$对应的特征值对角矩阵。
$$
U=[u_0,u_1,...,u_n]\\
\Lambda=\left[ \begin{matrix} \lambda_0 & 0 & 0 & ... & 0\\ 0 & \lambda_1 & 0 & ... & 0 \\ : & : & : &  & : \\ 0 & 0 & 0 & ... & \lambda_n \end{matrix} \right]
$$
图信号被定义为：
$$
x\in R^N
$$
是一个由图中各个结点组成的一个特征向量。$x_i$是其中第$i$个结点的信号值。

定义了图的信号，便可以对信号作傅里叶变换。图的傅里叶变换被定义为：
$$
\mathcal{F}(x)=U^T\hat{x}
$$
其意义是把特征向量的每个维度通过线性变化映射到另一组**正交基**所表示的空间中。符合傅里叶变换的本质（但仍然与一维连续信号的傅里叶变换定义不严格相同）。

根据傅里叶反变换的本质，图的傅里叶反变换即为：
$$
\mathcal{F^{-1}}(\hat{x})=Ux
$$
由于频域的乘积等于时域的卷积，因此可以用图傅里叶变换来定义图卷积：
$$
x*y=\mathcal{F^{-1}}(\mathcal{F}(x)\odot\mathcal{F}(y))=U(U^Tx\odot U^Ty)
$$
其中$\odot$即为Hadamard积。

基于二维图像的**空域**卷积范式——模板（卷积核），图网络可以定义一个滤波器作为图网络的卷积核：
$$
g_\theta=diag(U^Tg)
$$
其中$diag()$为对角线化函数。

那么对于图网络，我们也可以使用刚才定义的模板（卷积核）实现卷积操作：
$$
x*g_\theta=Ug_\theta U^Tx
$$


### 嵌入

一种特殊的全连接操作。其目的是数据降维。在NLP领域通常用于词向量（one-hot编码）的降维嵌入，同时还能隐形表示各个词向量之间的关联性。对于一些特殊的数据集也可以使用嵌入的方式对输入数据降维/提取特征。
$$
x_{in}=f_{emb}(x,\theta_{emb})
$$
其中$\theta_{emb}$是参数矩阵。

嵌入层常常设计为全连接层的形式（也有使用多层感知机的）。

### 注意力机制

注意力机制最先被应用于NLP领域的含遗忘门的RNN（长短期记忆，LSTM）编解码器模型中（碍于版面这里不再对LSTM编解码器模型这一模型进行详述）。用于这种sequence-to-sequence模型通过遗忘门的设计，具备了比simple-RNN更好的序列记忆能力。但是对于序列中的每个词，模型一视同仁，没有权重差别。注意力机制引入了序列输入中的权重差别。这项机制最后被用于Transformer模型，并击败了所有的更为复杂的RNN模型。因此可以认为正是注意力机制的出现使得Transformer模型成了为NLP领域state-of-the-art的模型。

如，RNN和Transformer模型中**每个单元**的注意力$c_j$可以被描述为:
$$
c_j=\sum^T_{i=1}\alpha_{ij}h_i
$$
其中，$\alpha$是权重矩阵中的注意力权重值，可以通过反向传播更新；$h_i$是每个单元的状态。

其中$\alpha$的计算方式如下：

![attention1](res/attention1.png)

![attention2](res/attention2.png)

transformer里面的attention：

![trans-attention1](res/trans-attention1.png)

![trans-attention2](res/trans-attention2.png)

self-attention：

假设当前已经在计算向量$h_k$的注意力$c_k$了，那么对于$h_k$,前面k个向量的权重$\alpha_i=align(h_i,h_k)$,由此一步步往前推，得到所有向量的注意力c

![self-attention](res/self-attention.png)

![self-attention2](res/self-attention2.jpg)

self-attention用来寻找内部关联性

Self-attention，transformer版：

![self-trans-attention1](res/self-trans-attention1.png)

![self-trans-attention2](res/self-trans-attention2.png)

可以见得，引入了注意力机制之后，模型的全局信息都被按权相加被浓缩在注意力值之中。这对于NLP领域的这两大拥有编解码器的模型而言，无疑是凸显重要信息的手段。因为注意力机制能更好的凸显关键信息，因此CV领域也逐渐引入视觉注意力。





### 半监督学习&直推式学习&归纳式学习概述

#### (1) 半监督学习

即原监督学习的训练集中有部分训练样本没有标签，且测试集**不存在**与训练集相同的样本。

训练集$\mathcal{D}$为：
$$
\mathcal{D}=\{X_{tr},y_{tr}|X_{un}\}
$$
同时测试集$X_{te}$满足：
$$
X_{te}\cap X_{un}=\emptyset
$$
监督学习基于平滑假设，即相似或相邻的样本点标签也应该相似。而半监督学习基于以下两种假设：

- **聚类假设**：是指同一聚类中的样本点很可能具有同样的类别标记。 这个假设可以通过另一种等价的方式进行表达，那就是决策边界所穿过的区域应当是数据点较为稀疏的区域，因为如果决策边界穿过数据点较为密集的区域那就很有可能将一个聚类中的样本点分为不同的类别这与聚类假设矛盾。
- **流型假设**是指高维中的数据存在着低维的特性。 、即“处于一个很小的局部邻域内的示例具有相似的性质”。 关于这两者的等价性没有严格的证明，但是高维数据中的数据的低维的特性是通过局部邻域相似性体现的，比如一个在三维空间卷曲的二维纸带，高维的数据全局的距离度量由于维度过高而显得没有区分度，但是如果只考虑局部范围的距离度量，那就会有一定意义。

这两种假设一般是一致的，属于监督学习中平滑假设的在半监督学习中的推广。

#### (2) 直推式学习

同半监督学习，但是测试集本身作为未标记的样本放入训练集进行训练。即测试集$X_{te}=X_{un}$。思路为**直推**，这种学习对目标任务具有较好的适应性，但对于整个样本空间所有可能出现的样本数据，泛化性能可能不如归纳式学习。

#### (3) 归纳式学习

即传统监督学习。使用完全标记的样本作为测试集，训练出一般性的模型，再进行未知数据的预测。思路为**归纳——演绎**，需要通过少量的数据推出普适性的模型来描述整个样本空间。



### 元学习&迁移学习概述

传统的机器学习研究模式是：获取特定任务的大型数据集，然后用这个数据集从头开始训练模型。很明显，这和人类利用以往经验，仅仅通过少量样本就迅速完成学习的情况相差甚远。（人类可以从少量样本中快速学习获取很大的认知能力，但算法模型则需要在大规模的数据集上得到训练才有可能达到人的识别能力）也就是说，人类具有**知识迁移**的能力。据此，提出元学习和迁移学习两种模型：

#### (1) 元学习

- 元学习重点在显性**寻找相似性**。（为什么是显性：因为模型的损失函数是基于同种数据跑出来的结果之间的差异）

- 使用原模型根据新Task生成适应的新模型，实现多任务的泛化。



#### (2) 迁移学习

- 迁移学习重点在隐性**迁移知识**。（为什么是隐形：因为参数迁移的时候是假定了这些参数能提取数据间的关联性）
- 通过不断将原模型迁移到新Task进行微调，实现多任务的泛化。



##### Fine-Tuning

 通常使用一个预训练网络的参数初始化另一个Task的网络。通常只Transfer前n层。最好情况是前n层的参数一样能被fine-tuning。最坏情况是只train最后几层，而固定Transfer过来的层不变。

用target训练出来的模型，固定前几层，后几层用source重新训练，结果也会更差

![fine-tuning](res/fine-tuning.png)

##### Multi-Task Learning

解决相似Task时，可以同时训练这些Task的数据。保留前几层相同，仅在最后层上做特化处理。（不同Task的数据，训练时所使用的最后几层各不相同，但是前几层的参数在训练过程中是完全一致的。）

![multi-task_learning1](res/multi-task_learning1.png)

![multi-task_learning2](res/multi-task_learning2.png)

##### Progressive Neural Network

递进的学习。不断得到新的网络。

过程是：把一个域的参数迁移到下一个域。每增加一个Task，就多新增拷贝+迁移得到一个解决新域的Task的网络。

注意：每个原Task域的网络参数不变，增加Task时相当于**多拷贝了一份**进行fine-tuning。

![progressive_learning](res/progressive_learning.png)

##### Domain Adaptation

即域自适应。用于解决相似或相同Task，但是域与域之间feature dismatch的情况。

通常这些domain的feature分布不均匀（例如source domain的feature分布零散，而target domain的feature分布集中，这样会导致分类器对source的分类效果很好，但是对target的分类很混淆）这个情况需要使用domain-adversarial结构进行domain adaptation。 

![domain-adaptation1](res/domain-adaptation1.png)

这个结构有点类似GAN：Domain classifier会尽力区分这些feature是否来源于同一个domain；Label predictor会尽力区分这些featrue的label；而feature extractor会尽力混淆这些feature使得domain classifer无法分辨、同时让Label predictor尽可能能够分辨featrue的label（即保留最多信息的同时混淆features的分布）

![domain-adaptation2](res/domain-adaptation2.png)

反向传播时，来自Domain classifer的参数值会乘一个负号。即反向传播到feature extractor时。不再是梯度下降，而是梯度上升（domain classfier 梯度下降让自己更能分辨；feature extractor梯度上升让domain classifier无法分辨）；而label predictor到feature extractor的梯度下降过程不变。



##### Zero-shot Learning

source data作为traning data，target data作为testing data。即traning中没有任何一个target的数据

解决方法是**找出比单个样本本身更小的单位**，例如某个图片是否具有某几个attributes。用特征的符合情况对数据归类。

![zero-shot_learning1](res/zero-shot_learning1.png)

通过attribute embedding层，使得每个图片对应的attribute经过嵌入后，和对应的图片通过image embedding之后在同一个嵌入向量空间中尽可能接近。这样输入testing data后，根据其在embedding空间中的位置，即可提取它的attribute，并且进行归类。

![zero-shot_learning2](res/zero-shot_learning2.png)

损失函数的思路是，让attribute和对应的image在embedding空间尽可能接近，同时与不同image尽可能远。（即元学习triplet网络的损失函数的思路）：
$$
f^*,g^*=\arg \min_{f,g}\sum_n\max(0,k-f(x^n)\cdot g(x^n)+\max_{m\ne n}f(x^n)\cdot g(y^m))\\
$$
即：
$$
f(x^n)\cdot g(x^n)-\max_{m\ne n}f(x^n)\cdot g(y^m)>k
$$
的时候才是最好的（zero-loss）。如果不同图片的向量之间相互正交，那就再好不过了（点乘=0）

https://zhuanlan.zhihu.com/p/50710267

https://www.infoq.cn/article/b40tCBfQ-paDPDz5ZQzl



### 实验

在试验阶段，我们通常使用一些领域内常见的dataset做benchmark。通过对比这些领域内baseline的效果、（甚至）领域内state-of-the-art的效果与我们论文提出的论文的效果，来凸显我们模型的优越性。

#### (1)Baseline

Baseline通常是某个领域的**最常用模型**，是一系列模型比较中的**参照标准**。与Baseline的效果进行对比，能说明我们模型的优化方向是否正确（或者有没有反向优化等）。backbone是在finetuning中使用的主干网络

#### (2)Benchmark

这个在不同方面代表不同的意思，一般指**具体实验的载体**，在CV中主要指DataSet,**某一类数据集**用来实验某一项研究，如当前比较火的Meta-learning中的Omniglot,就是一个多种类，单个种类样本却很少的数据集。专门用来玩few shot learning或者 one shot learning.或者专门用来做视频的UTF101,moving-mnist，就是视频类文章的benchmark

#### (3)Backbone

主要是指某一种**基干网络**，比如比较主流网络残差resnet,对抗生成gan,然后在基干网络上加东西或者改东西。

-----------------------------------------------------

迁移学习相关的Benchmark和其baseline请参考https://github.com/jindongwang/transferlearning/blob/master/data/benchmark.md

---







## Project

### 调研

#### 初始化和重塑网络

参考：https://pytorch.apachecn.org/docs/1.0/finetuning_torchvision_models_tutorial.html

> 现在来到最有趣的部分。在这里我们对每个网络进行重塑。请注意，这不是一个自动过程，并且对每个模型都是唯一的。 回想一下，CNN模型的最后一层(通常是FC层）与数据集中的输出类的数量具有相同的节点数。 由于所有模型都已在Imagenet上预先训练，因此它们都具有大小为1000的输出层，每个类一个节点。 这里的目标是将最后一层重塑为与之前具有相同数量的输入，并且具有与数据集中的类别数相同的输出数。 在以下部分中，我们将讨论如何更改每个模型的体系结构。 但首先，有一个关于微调和特征提取之间差异的重要细节。
>
> 当进行特征提取时，我们只想更新最后一层的参数，换句话说，我们只想更新我们正在重塑层的参数。 因此，我们不需要计算不需要改变的参数的梯度，因此为了提高效率，我们将其它层的.requires_grad属性设置为False。 这很重要，因为默认情况下，此属性设置为True。 然后，当我们初始化新层时，默认情况下新参数`.requires_grad = True`，因此只更新新层的参数。 当我们进行微调时，我们可以将所有.required_grad设置为默认值True。
>
> 最后，请注意inception_v3的输入大小为(299,299），而所有其他模型都输入为(224,224）。

图片transform预处理操作参考https://blog.csdn.net/theVicTory/article/details/109230519

### 超参数选取

#### Learning Rate

Learning Rate通常用0.01

`optimizer.step()`会自动优化学习率。所以不用太拘泥于LR的选择

#### Batch

Batch 通常用128

1. Batch数太小，可能会导致loss函数震荡而不收敛，尤其是在网络比较复杂的时候
2. 随着batchsize增大，达到相同精度所需要的epoch数量越来越多

#### Epoch

Epoch通常用10

1. Epoch太大会导致过拟合
2. Epoch太小会导致欠拟合

#### 如何选择

当训练开始时，若：

- Loss不震荡（收敛）
- Acc有明显上升（速度够快）

Batch就可以确定下来了

当训练结束时，若：

- Loss不再怎么下降（收敛）
- Train Acc和Val Acc差距不太大（没有过拟合）

Epoch就可以确定下来了

### 基准

#### 参考

|               | Datasets                                                     | Pretrained Models                                            |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Datasets      |                                                              | ResNet18                                                     |
| Caltech-256   | https://robustnessws4285631339.blob.core.windows.net/public-datasets/caltech256.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/TropComplique/image-classification-caltech-256/blob/master/resnet/train18.ipynb       https://github.com/PKUAI26/AT-CNN/blob/master/code/baseline/main.py |
| CIFAR-100     |                                                              | https://github.com/weiaicunzai/pytorch-cifar100              |
| DTD           | https://robustnessws4285631339.blob.core.windows.net/public-datasets/dtd.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/microsoft/robust-models-transfer          |
| Flowers102    | https://robustnessws4285631339.blob.core.windows.net/public-datasets/flowers.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | [https://github.com/Muhammad-MujtabaSaeed/102-Flowers-Classification/blob/master/102_Flowers_classification.ipynb            https://github.com/microsoft/robust-models-transfer](https://github.com/Muhammad-MujtabaSaeed/102-Flowers-Classification/blob/master/102_Flowers_classification.ipynb) |
| Pets          | https://robustnessws4285631339.blob.core.windows.net/public-datasets/pets.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/microsoft/robust-models-transfer          |
| Sun397        | https://robustnessws4285631339.blob.core.windows.net/public-datasets/SUN397.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/microsoft/robust-models-transfer          |
| SVHN          | http://ufldl.stanford.edu/housenumbers/                      | https://github.com/codyaustun/pytorch-resnet                 |
| Food          | https://robustnessws4285631339.blob.core.windows.net/public-datasets/food.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/alvarobartt/serving-pytorch-models/blob/master/notebooks/transfer-learning.ipynb |
| Aircraft      | https://robustnessws4285631339.blob.core.windows.net/public-datasets/fgvc-aircraft-2013b.tar.gz?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/microsoft/robust-models-transfer          |
| Birds         | https://robustnessws4285631339.blob.core.windows.net/public-datasets/birdsnap.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/microsoft/robust-models-transfer          |
| Stanford_Cars | https://robustnessws4285631339.blob.core.windows.net/public-datasets/stanford_cars.tar?sv=2019-10-10&ss=b&srt=sco&sp=rlx&se=2021-10-05T15:06:23Z&st=2020-06-10T07:06:23Z&spr=https&sig=Rwwsg9yfcSrbNLvxse%2F32XOy7ERWSLXMz9Ebka4pS20%3D | https://github.com/microsoft/robust-models-transfer          |



#### FT

仅仅是做multi-source的fine tuning罢了

取三个模型的最大准确率为最终准确率

#### Ensemble

做output的集成，用一些比较简单的方法

在每一个分类的维度上，取三个模型的output的最大置信度（或者均值），作为该分类的置信度（0～1之间）

最后输出output里面，每个分类的维度都是三个模型认为的最大置信度值（或者均值）。

#### Attention

使用注意力机制对Multi-Source的输出做加权，然后再通过全链接层做分类。

#### KDE

KDE即**核密度估计**



#### 测试结果

**Structure:**ResNet18

**Source:**ImageNet+Caltech256+Cifar100

**Target:**Cifar10

|        Method         | Validation |  Test  |
| :-------------------: | :--------: | :----: |
|      FT-ImageNet      |   0.9506   | 0.9412 |
|     FT-Caltech256     |   0.9514   | 0.9484 |
|      FT-Cifar100      |   0.9512   | 0.9506 |
|     Ensemble-max      |   0.9552   | 0.9518 |
|     Ensemble-mean     |   0.9620   | 0.9572 |
|     Attention-RNN     |   0.9462   | 0.9302 |
| Attention-Transformer |   0.9496   | 0.9428 |
|    Self-Attention     |   0.9478   | 0.9408 |
|          KDE          |            |        |
|        MS-SVM         |            | 0.9297 |
|         MS-FC         |            | 0.9253 |





## TODO List 进度列表

1. 好像只有源码，没有模型。

   >使用老师给的+网上找的+自己跑的 预训练模型

2. torchvision提供的预训练模型都是用ImageNet-1k训练好的

   > 只要架构，不要参数，尤其是全链接层

3. 直接使用预训练模型，最后一层全链接层输出的**class数**是固定的。

   >需要手动更改最终输出的**class数量**，参考https://blog.csdn.net/andyL_05/article/details/108930240提供的解释:
   >
   >>在分类问题上，模型的最后一层一般是一个全连接层，输出的神经元个数就是类别信息，最后输出结果是一个浮点向量，大小表示某一类别的可能性，数值越大说明越倾向于分为该类。
   >>显然直接使用预训练的网络不加修改那么总类别数就是固定的，当我们使用的场景类别数不一致时，就要自行修改模型的最后一层。

4. 可以手动访问预训练网络的某些层，来更改其结构

   ```python
   from torch import nn
   res18 = models.resnet101(pretrained=True)
   numFit = res18.fc.in_features
   
   res18.fc = nn.Linear(numFit, numClass)
   
   # res18.fc = nn.Sequential(nn.Linear(numFit, numClass), nn.Softmax(dim=1))
   ```

   这里也可以十分贴心的提供了softmax，使得最终输出的就是概率分布。

5. 在用torchvision提供的resnet18模型对caltech256数据集进行测试的时候碰到了几个问题：

>1. 预训练模型使用的source的class和target的class不能完全对应。target里面有些class，在source里面是没有的。这种情况，是不是不该对target中这些source里面不存在的class进行分类呢？
>
>2. source的class映射的类编号可能和target的class映射的类编号不同（model的数值label不同）
>
>以上两个问题会不会导致模型没有意义呢
>
>> **pretrained model是用来提取feature的网络罢了**
>>
>>- target data通过pre-trained model 输出的向量，仅仅只是**作为feature**（其实际意义大概是“**更接近原先source中某个class的程度**”）。这些feature提供给后续的SVM做分类的时候使用。
>>- 这样SVM可能会得到一些来自pre-trained model提取的feature信息。而target中，相同的class可能会**共享部分feature**，这会使得SVM分类器**更倾向于把他们归为一类**。
>>- 现在跑baseline，是每次**仅使用一个pre-trained model**的SVM分类的效果

6. 为什么resnet等最后一层都是fc而非softmax：**仅针对使用该模型直接进行分类的情况**

> 1. 因为softmax保序性，可以与model解耦。可以得到logits之后再softmax+argmax，会省略很多时间（或者直接用argmax）
> 2. logits计算指数再归一化的计算量比较大。尤其是在模型训练中，softmax的计算完全是没有意义的，完全可以只在测试时做softmax。
> 3. 参考https://www.zhihu.com/question/456082205

7. 注意pytorch里面默认向量是列向量。即dim=0是指的列那一个维度

8. features**需要normalize**
9. Finish the KDE
10. Visualize the attention weights
11. Re-implement our simple algorithm (+SVM) again:SVM->FC





## Reference

