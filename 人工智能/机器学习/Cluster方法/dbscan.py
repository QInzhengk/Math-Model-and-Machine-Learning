import numpy as np
import math as m
import evaluate as eva
import matplotlib.pyplot as plt
import queue

# flame.txt
# Jain_cluster=2.txt
# Aggregation_cluster=7.txt
# Spiral_cluster=3.txt
# Pathbased_cluster=3.txt

data_path = "data\\ws_Lat_Lon.txt"
NOISE = 0
UNASSIGNED = -1


def load_data():
    """
    导入数据
    :return: 数据
    """
    points = np.loadtxt(data_path, delimiter='\t',usecols=(1,2))
    return points


def dist(a, b):
    """
    计算两个向量的距离
    :param a: 向量1
    :param b: 向量2
    :return: 距离
    """
    return m.sqrt(np.power(a-b, 2).sum())


def neighbor_points(data, pointId, radius):
    """
    得到邻域内所有样本点的Id
    :param data: 样本点
    :param pointId: 核心点
    :param radius: 半径
    :return: 邻域内所用样本Id
    """
    points = []
    for i in range(len(data)):
        if dist(data[i, 0: 2], data[pointId, 0: 2]) < radius:
            points.append(i)
    return np.asarray(points)


def to_cluster(data, clusterRes, pointId, clusterId, radius, minPts):
    """
    判断一个点是否是核心点，若是则将它和它邻域内的所用未分配的样本点分配给一个新类
    若邻域内有其他核心点，重复上一个步骤，但只处理邻域内未分配的点，并且仍然是上一个步骤的类。
    :param data: 样本集合
    :param clusterRes: 聚类结果
    :param pointId:  样本Id
    :param clusterId: 类Id
    :param radius: 半径
    :param minPts: 最小局部密度
    :return:  返回是否能将点PointId分配给一个类
    """
    points = neighbor_points(data, pointId, radius)
    points = points.tolist()

    q = queue.Queue()

    if len(points) < minPts:
        clusterRes[pointId] = NOISE
        return False
    else:
        clusterRes[pointId] = clusterId
    for point in points:
        if clusterRes[point] == UNASSIGNED:
            q.put(point)
            clusterRes[point] = clusterId

    while not q.empty():
        neighborRes = neighbor_points(data, q.get(), radius)
        if len(neighborRes) >= minPts:                      # 核心点
            for i in range(len(neighborRes)):
                resultPoint = neighborRes[i]
                if clusterRes[resultPoint] == UNASSIGNED:
                    q.put(resultPoint)
                    clusterRes[resultPoint] = clusterId
                elif clusterRes[clusterId] == NOISE:
                    clusterRes[resultPoint] = clusterId
    return True


def dbscan(data, radius, minPts):
    """
    扫描整个数据集，为每个数据集打上核心点，边界点和噪声点标签的同时为
    样本集聚类
    :param data: 样本集
    :param radius: 半径
    :param minPts:  最小局部密度
    :return: 返回聚类结果， 类id集合
    """
    clusterId = 1
    nPoints = len(data)
    clusterRes = [UNASSIGNED] * nPoints
    for pointId in range(nPoints):
        if clusterRes[pointId] == UNASSIGNED:
            if to_cluster(data, clusterRes, pointId, clusterId, radius, minPts):
                clusterId = clusterId + 1
    return np.asarray(clusterRes), clusterId


def plotRes(data, clusterRes, clusterNum):
    nPoints = len(data)
    scatterColors = ['black', 'blue', 'green', 'yellow', 'red', 'purple', 'orange', 'brown']
    for i in range(clusterNum):
        color = scatterColors[i % len(scatterColors)]
        x1 = [];  y1 = []
        for j in range(nPoints):
            if clusterRes[j] == i:
                x1.append(data[j, 0])
                y1.append(data[j, 1])
        plt.scatter(x1, y1, c=color, alpha=1, marker='+')


if __name__ == '__main__':
    data = load_data()
    cluster = np.asarray(data[:, 1])
    clusterRes, clusterNum = dbscan(data, 0.8, 3)
    plotRes(data, clusterRes, clusterNum)
    nmi, acc, purity = eva.eva(clusterRes, cluster)
    print(nmi, acc, purity)
    plt.show()