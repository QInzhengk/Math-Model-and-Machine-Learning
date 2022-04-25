from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
%matplotlib inline
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
#pca降维
def pca_analyze(data):
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
    #pca降维，选择解释度和为0.95的因子
    print("\n选择累计贡献率大于等于0.95的因子")
    pca = PCA(n_components=0.95)
    df_d = pca.fit_transform(data)
    df_ev = pca.explained_variance_
    df_evr = pca.explained_variance_ratio_
    df_evr_sum = np.cumsum(pca.explained_variance_ratio_)
    df_fa = pd.DataFrame(
            {'特征值': df_ev, '方差贡献率': df_evr,'方差累计贡献率': df_evr_sum})
    print(df_fa)
    k1_spss = pca.components_ / np.sqrt(pca.explained_variance_.reshape(-1, 1))  # 成分得分系数矩阵
    k1_spss = pd.DataFrame(k1_spss.T)
    print("\n成分得分系数矩阵: \n",k1_spss)
    tmp_columns = []
    for index in range(df_ev.shape[0]):
       tmp = "factor" + str(index + 1)
       tmp_columns.append(tmp)
    k1_spss.columns = tmp_columns
    print("\n主成分得分",k1_spss)
    print("\n==============采用熵权法计算各个因子的权重===============")
    fa_t_score = np.dot(np.mat(data), np.mat(k1_spss))
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