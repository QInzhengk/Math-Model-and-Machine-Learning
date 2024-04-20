import numpy as np
from ThreadWithReturn import *
import math as m
import random
import matplotlib.pyplot as plt
import evaluate as eva
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
# flame.txt
# Jain_cluster=2.txt
# Aggregation_cluster=7.txt
# Spiral_cluster=3.txt
# Pathbased_cluster=3.txt

#data_path = "data\\Aggregation_cluster=7.txt"
data_path = "data\\user_Lat_Lon.txt"

# 导入数据
def load_data():
    points = np.loadtxt(data_path, delimiter='\t')
    return points


def cal_dis(data, clu, k):
    """
    计算质点与数据点的距离
    :param data: 样本点
    :param clu:  质点集合
    :param k: 类别个数
    :return: 质心与样本点距离矩阵
    """
    dis = []
    for i in range(len(data)):
        dis.append([])
        for j in range(k):
            dis[i].append(m.sqrt((data[i, 1] - clu[j, 0])**2 + (data[i, 2]-clu[j, 1])**2))
    return np.asarray(dis)


def divide(data, dis):
    """
    对数据点分组
    :param data: 样本集合
    :param dis: 质心与所有样本的距离
    :param k: 类别个数
    :return: 分割后样本
    """
    clusterRes = [0] * len(data)
    for i in range(len(data)):
        seq = np.argsort(dis[i])
        clusterRes[i] = seq[0]

    return np.asarray(clusterRes)


def center(data, clusterRes, k):
    """
    计算质心
    :param group: 分组后样本
    :param k: 类别个数
    :return: 计算得到的质心
    """
    clunew = []
    for i in range(k):
        # 计算每个组的新质心
        idx = np.where(clusterRes == i)
        sum = data[idx].sum(axis=0)
        avg_sum = sum/len(data[idx])
        clunew.append(avg_sum)
    clunew = np.asarray(clunew)
    return clunew[:, 1: 3]


def classfy(data, clu, k):
    """
    迭代收敛更新质心
    :param data: 样本集合
    :param clu: 质心集合
    :param k: 类别个数
    :return: 误差， 新质心
    """
    clulist = cal_dis(data, clu, k)
    clusterRes = divide(data, clulist)
    clunew = center(data, clusterRes, k)
    err = clunew - clu
    return err, clunew, k, clusterRes


def plotRes(data, clusterRes, clusterNum):
    """
    结果可视化
    :param data:样本集
    :param clusterRes:聚类结果
    :param clusterNum: 类个数
    :return:
    """
    nPoints = len(data)
    scatterColors = ['black', 'blue', 'green', 'yellow', 'red', 'purple', 'orange', 'brown']
    for i in range(clusterNum):
        color = scatterColors[i % len(scatterColors)]
        x1 = [];  y1 = []
        for j in range(nPoints):
            if clusterRes[j] == i:
                x1.append(data[j, 1])
                y1.append(data[j, 2])
        plt.scatter(x1, y1, c=color, alpha=1, marker='+')
    plt.show()

def DataFrame2Matrix(n_users, n_items, dataframe):
    train_data_matrix = np.zeros((n_users, n_items))
    for line in dataframe.itertuples():
        train_data_matrix[line[1], line[2]] = line[3]
    return train_data_matrix

def getSimility(i,lista):
    SimilityMatrix=None 
    datapath="data\\rt.txt"
    data = pd.read_csv(datapath,sep="\t",names=['user_id', 'item_id', 'rating'], engine='python') 
    data = pd.DataFrame(data)
    test1 = ThreadWithReturnValue(target=DataFrame2Matrix, args=(339, 5825, data))
    test1.start()
    data_matrix = test1.join()
    SimilityMatrix = cosine_similarity(data_matrix)
    sumSimility=0
    num=0
    for j in lista:
        sumSimility=sumSimility+SimilityMatrix[i][j]
        num=num+1
    ave=sumSimility/num
    print(ave)

if __name__ == '__main__':
    k = 7                                          # 类别个数
    data = load_data()
    clu = random.sample(data[:, 1:3].tolist(), k)  # 随机取质心
    clu = np.asarray(clu)
    err, clunew,  k, clusterRes = classfy(data, clu, k)
    while np.any(abs(err) > 0):
        print(clunew)
        err, clunew,  k, clusterRes = classfy(data, clunew, k)

    clulist = cal_dis(data, clunew, k)
    clusterResult = divide(data, clulist)
    
    i=0
    
    for b in range(339):
        if(clusterResult[b]==1):
            i=b
            break
    
    list1=[]
    for a in range(339):
        if(clusterResult[a]==1):
            list1.append(a)
    getSimility(i,list1)
    
    
    list2=[]
    for c in range(339):
        if(clusterResult[c]==2):
            list2.append(c)
    getSimility(i,list2)

    list3=[]
    for d in range(339):
        if(clusterResult[d]==3):
            list3.append(d)
    getSimility(i,list3)
    
    list4=[]
    for f in range(339):
        if(clusterResult[f]==4):
            list4.append(f)
    getSimility(i,list4)

    list5=[]
    for g in range(339):
        if(clusterResult[g]==5):
            list5.append(g)
    getSimility(i,list5)
    
    list6=[]
    for k in range(339):
        if(clusterResult[k]==6):
            list6.append(k)
    getSimility(i,list6)

    list7=[]
    for l in range(339):
        if(clusterResult[l]==0):
            list7.append(l)
    getSimility(i,list7)     
    #nmi, acc, purity = eva.eva(clusterResult, np.asarray(data[:, 2]))
    #print(nmi, acc, purity)
    plotRes(data, clusterResult, k)