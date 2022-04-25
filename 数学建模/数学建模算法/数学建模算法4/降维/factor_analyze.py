from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
from factor_analyzer.factor_analyzer import calculate_kmo
from factor_analyze import Factor_analyzer
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
%matplotlib inline
sns.set(font_scale=1.5)

#熵权法
def get_entropy_weight(data):
    """
    :param data: 评价指标数据框
    :return: 各指标权重列表
    """ 
    data = pd.DataFrame(data)
    data = data.apply(lambda data: ((data - np.min(data)) / (np.max(data) - np.min(data))))
    #计算k
    m,n=data.shape   #m是行，n是列
    yij=np.array(data.sum(axis=0))  
    data = np.array(data)
    #计算pij
    pij=np.array(data/yij)
    a=pij*1.0
    a[np.where(pij==0)]=0.0001
#    #计算每个指标的熵
    e=(-1.0/np.log(n))*np.sum(pij*np.log(a),axis=0)
    w=(1-e)/np.sum(1-e)
    recodes=np.sum(data*w,axis=1)
    return recodes
# 因子分析
def Factor_analyzer(data):
    """
    :param data: 原始数据
    :return: 所有样本的综合得分，前十大恐怖事件ID
    """ 
    print("\n原始数据:\n",data)
    #归一化
    data = (data-data.mean())/data.std()  
    print("\n归一化之后的数据:\n",pd.DataFrame(data))
    # 皮尔森相关系数
    data_corr=data.corr()
    print("\n相关系数:\n",pd.DataFrame(data_corr))
    #热力图
    cmap = cm.Blues
    sns.set()
    plt.figure(figsize=(10, 10))
    ax = sns.heatmap(data=data_corr,square=True,cmap=cmap, vmin=0, vmax=1) 
    plt.title('correlation coefficient--headmap')
    ax.set_yticks(range(len(data_corr.columns)))
    ax.set_yticklabels(data_corr.columns)
    ax.set_xticks(range(len(data_corr)))
    ax.set_xticklabels(data_corr.columns)
    plt.show()
    # KMO测度,0.9以上非常好；0.8以上好；0.7一般；0.6差；0.5很差；0.5以下不能接受；
    kmo_all,kmo_model=calculate_kmo(data)
    print("\nKMO测度:", kmo_model)
    if kmo_model < 0.6:
        print("\nKMO测度不足0.6，不适合做因子分析")
    else:
        print("\nKMO测度大于0.6，适合做因子分析")
    #Bartlett's球状检验,用来判断变量是否适合用于做因子分析
    #Bartlett球度统计量越大越好，其伴随概率<0.05，说明数据适合做因子分析
    chi_square_value,p_value=calculate_bartlett_sphericity(data)
    print("\n巴特利特球形检验:",p_value)
    if p_value > 0.05:
        print("\n巴特利特球形检验的伴随概率大于0.05，不适合做因子分析")
    else:
        print("\n巴特利特球形检验的伴随概率小于0.05，适合做因子分析")
     # 求特征值和特征向量
    fa = FactorAnalyzer(n_factors = 25,rotation=None)
    fa.fit(data_corr)
    ev, v = fa.get_eigenvalues()
    print("\n特征值:",ev)
    print("\n特征向量",v)
    #绘制碎石图，选取特征值大于1的因子
    print("\n=================绘制碎石图==================")
    plt.figure(figsize=(6, 6))
    plt.scatter(range(1,data.shape[1]+1),ev)
    plt.plot(range(1,data.shape[1]+1),ev)
    plt.title('Scree Plot')
    plt.xlabel('Factors')
    plt.ylabel('Eigenvalue')
    plt.grid()
    plt.show()
    m = 0
    for i in range(len(ev)):
        if ev[i] > 1:
            m = m+1;
        else:
            break;
    print("由碎石图可知有" + str(m) +"个因子的特征值大于1，所以选择" + str(m) +"个因子重新进行因子分析")
    #根据选择的因子数重新执行因子分析
    #使用最大方差法旋转因子载荷矩阵
    fa = FactorAnalyzer(n_factors = m,rotation='varimax')
    fa.fit(data_corr)
    load = fa.loadings_
    #旋转后的因子的载荷矩阵
    print("\n旋转后的因子荷载矩阵",load)
    fa_var = fa.get_factor_variance()
    fa_df = pd.DataFrame(
        {'特征值': fa_var[0], '方差贡献率': fa_var[1], '方差累计贡献率': fa_var[2]})
    print(fa_df)
     # 因子得分（回归方法）（系数矩阵的逆乘以因子载荷矩阵）
    print("\n==========以下采用回归方法计算因子得分============")
    X1 = np.mat(data_corr)
    X1 = np.linalg.inv(X1)
    factor_score = np.dot(X1,load)
    factor_score = pd.DataFrame(factor_score)
    tmp_columns = []
    for index in range(m):
       tmp = "factor" + str(index + 1)
       tmp_columns.append(tmp)
    factor_score.columns = tmp_columns
    print("\n因子得分",factor_score)
    print("\n==============采用熵权法计算各个因子的权重===============")
    fa_t_score = np.dot(np.mat(data), np.mat(factor_score))
    w = get_entropy_weight(fa_t_score.T)
    print("\n熵权法求得的权重为：\n",w)
    fa_t_score = np.dot(fa_t_score,w)
    fa_t_score = pd.DataFrame(fa_t_score.T)
    print("\n各个样本得分如下：\n",fa_t_score)
    fa_t_score.columns = ['综合得分']
    fa_t_score.insert(0, 'ID', range(0, data.shape[0]))
    top10 = fa_t_score.sort_values(by='综合得分', ascending=False).head(10)
    index = top10.ID
    print("\n前十大事件综合得分：\n", fa_t_score.sort_values(by='综合得分', ascending=False).head(10))
    return fa_t_score,index
            
    

        
        
        