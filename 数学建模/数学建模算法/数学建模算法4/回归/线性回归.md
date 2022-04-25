# 线性回归算法

线性回归算法是使用线性方程对数据集拟合的算法

- 多元线性回归
- 多项式回归（非线性）
- 神经网络+ensemble

### 多变量（多元） 线性回归

即多个输入特征。此时输出y的值由n个输入特征 $x_{1}, x_{2}, \ldots, x_{n}$ 决定。那么预测函数模型可以改写如下：

$$ h_{\theta}(x)=\theta_{0}+\theta_{1} x_{1}+\theta_{2} x_{2}+\ldots+\theta_{n} x_{n} $$ 假设 $x_{0}=1$，那么上面的公式可以重写为： $$
h_{\theta}(x)=\sum_{j=0}^{n} \theta_{j} x_{j} $$ 其中，$\theta_{0}, \theta_{1}, \dots, \theta_{n}$ 统称为 $\theta$ ,
是预测函数的参数。即一组 $\theta$ 值就决定了一个预测函数，记为 $h_{\theta}(x)$ , 为了简便起见，在不引起误解的情况下可以简写为 $h(x)$ 。理论上，预测函数有无穷多个，我们求解的目标就是找出一个最优的
$\theta$ 值。

#### 向量形式的预测函数

根据向量乘法运算法则，损失函数可重写为：

$$ h_{\theta}(x)=\left[\theta_{0}, \theta_{1}, \cdots, \theta_{n}\right]
\left[\begin{array}{c} x_{0} \\ x_{1} \\ \vdots \\ x_{n} \end{array}\right]=\theta^{T} x $$ 此处，依然假设 $x_{0}=1$， $x_{0}$
称为模型偏置（bias）。

写成向量形式的预测函数有两个原因。一是因为简洁，二是因为在实现算法时，要用到数值计算里的矩阵运算来提高效率，比如 `Numpy` 库里的矩阵运算。

#### 向量形式的训练样本

假设输入特征的个数是n，即 $x_{1}, x_{2}, \ldots, x_{n}$ , 我们总共有 m 个训练样本，为了书写方便，假设 $x_{0}=1$。这样训练样本可以写成矩阵的形式，即矩阵里每一行都是一个训练样本，总共有 m
行，每行有 n+1 列。

$$
\boldsymbol{X}=\left[\begin{array}{ccccc} x_{0}^{(1)} & x_{1}^{(1)} & x_{2}^{(1)} & \dots & x_{n}^{(1)} \\ x_{0}^{(2)} & x_{1}^{(2)} & x_{2}^{(2)} & \dots & x_{n}^{(2)} \\ \vdots & \vdots & \vdots & \ddots & \vdots \\ x_{0}^{(m)} & x_{1}^{(m)} & x_{2}^{(m)} & \cdots & x_{n}^{(m)} \end{array}\right]
, \theta=\left[\begin{array}{c} \theta_{0} \\ \theta_{1} \\ \theta_{2} \\ \vdots \\ \theta_{n} \end{array}\right]
$$

理解训练样本矩阵的关键在于理解这些上标和下标的含义。其中，带括号的上标表示样本序号，从1到m；下标表示特征序号，从0到n，其中 $x_{0}$ 为常数1。

> $x_{j}^{(i)}$ 表示第 i 个训练样本的第 j 个特征的值。而 $x^{(i)}$ 只有上标，则表示第 i 个训练样本所构成的列向量。

综上，训练样本的预测值 $h_{\theta}(X)$ ，可以使用下面的矩阵运算公式：

$$ h_{\theta}(X)=X \theta $$

#### 损失函数

多变量线性回归算法的损失函数：

$$ J(\theta)=\frac{1}{2 m} \sum_{i=1}^{m}\left(h\left(x^{(i)}\right)-y^{(i)}\right)^{2} $$ 其中，模型参数 $\theta$ 为 n+1
维的向量，$h\left(x^{(i)}\right)-y^{(i)}$ 是预测值和实际值的差，这个形式和单变量线性回归算法的类似。

损失函数有其对应的矩阵形式： $$ J(\theta)=\frac{1}{2 m}(X \theta-\vec{y})^{T}(X \theta-\vec{y})
$$ 其中，X 为 $m \times(n+1)$ 维的训练样本矩阵；上标T表示转置矩阵；$\vec{y}$ 表示由所有的训练样本的输出 $y^{(i)}$
构成的向量。这个公式的优势是：没有累加器，不需要循环，直接使用矩阵运算，就可以一次性计算出对特定的参数 $\theta$ 下模型的拟合损失。

#### 梯度下降算法

根据单变量线性回归算法的介绍，梯度下降的公式为： $$ \theta_{j}=\theta_{j}-\alpha \frac{\partial}{\partial \theta_{j}} J(\theta)
$$ 公式中，下标 j 是参数的序号，其值从 0 到 n； $\alpha$ 为学习率。把损失函数代入上式，利用偏导数计算法则，不难推导出梯度下降算法的参数迭代公式： $$ \theta_{j}=\theta_
{j}-\frac{\alpha}{m} \sum_{i=1}^{m}\left(\left(h\left(x^{(i)}\right)-y^{(i)}\right) x_{j}^{(i)}\right)
$$ 我们可以对比一下单变量线性回归函数的参数迭代公式。实际上和多变量线性回归函数的参数迭代公式是一模一样的。惟一的区别就是因为 $x_{0}$ 为常数1，在单变量线性回归算法的参数迭代公式中省去了。

应用这个公式编写机器学习算法，一般步骤如下：

- 确定学习率： $\alpha$ 太大可能会使损失函数无法收敛，太小则计算太多，机器学习算法效率就比较低。

- 参数初始化：比如让所有的参数都以1作为起始点，$\theta_{0}=1, \theta_{1}=1, \dots, \theta_
  {n}=1$，根据预测值和损失函数，就可以算出在参数起始位置的损失。需要注意的是，参数起始点可以根据实际情况灵活选择，以便让机器学习算法的性能更高，比如选择比较靠近极点的位置。

- 计算参数的下一组值：据梯度下降参数迭代公式，分别同时计算出新的 $\theta_{j}$ 值，进而得到新的预测函数 $h_{\theta}(x)$ 。再根据新的预测函数，代入损失函数就可以算出新的损失。

-

确定损失函数是否收敛：拿新的和旧的损失进行比较，看损失是不是变得越来越小。如果两次损失之间的差异小于误差范围，即说明已经非常靠近最小损失了，就可以近似地认为我们找到了最小损失。如果两次损失之间的差异在误差范围之外，重复步骤（3）继续计算下一组参数直到找到最优解。

```python
from sklearn.linear_model import LinearRegression
lr = LinearRegression()
lr.fit(X_train, Y_train)
```

### 多项式线性回归

当线性回归模型太简单导致欠拟合时，我们可以增加特征多项式来让线性回归模型更好地拟合数据。比如有两个特征 $x_{1}$ 和 $x_{2}$ ，可以增加两个特征的乘积 $x_{1} \times x_{2}$ 作为新特征 $x_{3}$
。同理，我们也可以增加 $x_{1}^{2}$ 和 $x_{2}^{2}$ 分别作为新特征 $x_{4}$ 和 $x_{5}$ 。

在 `scikit-learn` 里，线性回归是由类 `sklearn.learn_model.LinearRegression` 实现的，多项式由类`sklearn.preprocessing.PolynomialFeatures`
实现。那么要怎样添加多项式特征呢？我们需要用一个管道把两个类串起来，即用 `sklearn.pipeline.Pipeline` 把这两个模型串起来。

比如下面的函数就可以创建一个多项式拟合：

```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
def polynomial_model(degree=1):
    polynomial_features = PolynomialFeatures(degree=degree,include_bias=False)
    linear_regression = LinearRegression(normalize=True)
    # 这是一个流水线，先增加多项式阶数，然后再用线性回归算法来拟合数据
    pipeline = Pipeline([("polynomial_features", polynomial_features),
                         ("linear_regression", linear_regression)])
    return pipeline
```

一个 Pipeline 可以包含多个处理节点，在 scikit-learn 里，除了最后一个节点外，其他的节点都必须实现 fit() 方法和 transform() 方法，最后一个节点只需要实现 fit() 方法即可。当训练样本数据送进
Pipeline 里进行处理时，它会逐个调用节点的 fit() 方法和 transform() 方法，最后调用最后一个节点的 fit() 方法来拟合数据。

```python
poly_model = polynomial_model(degree=2)
poly_model.fit(X_train, Y_train)
```

### 神经网络回归

https://ensemble-pytorch.readthedocs.io/en/stable/introduction.html

一个写好的包，可以用来分类和回归，最重要的是有ensemble 方法，具体用法可以看api和我的jupyter

![image-20210724120021787](https://gitee.com/ma_tung_zhou/imageuse1/raw/master/imgg/image-20210724120021787-1627103229681.png)

## jupyter文档目录

![image-20210724130215238](https://gitee.com/ma_tung_zhou/imageuse1/raw/master/imgg/image-20210724130215238-1627103219820.png)







