import numpy as np
import random
import math
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.datasets import load_iris


# def InitCentroids(X, K):
#     n = np.size(X, 0)
#     rands_index = np.array(random.sample(range(1, n), K))
#     centriod = X[rands_index, :]
#     return centriod

def InitCentroids(x, K):   ###kmeans++ 选取初始值的方式
    c0_idx = int(np.random.uniform(0, len(x)))
    centroid = x[c0_idx].reshape(1, -1)  # 选择第一个簇中心
    k = 1
    n = x.shape[0]
    while k < K:
        d2 = []
        for i in range(n):
            subs = centroid - x[i, :]
            dimension2 = np.power(subs, 2)
            dimension_s = np.sum(dimension2, axis=1)  # sum of each row
            d2.append(np.min(dimension_s))
        new_c_idx = np.argmax(d2)
        centroid = np.vstack([centroid, x[new_c_idx]])
        k += 1
    return centroid


def findClosestCentroids(X, w, centroids):
    K = np.size(centroids, 0)
    idx = np.zeros((np.size(X, 0)), dtype=int)
    n = X.shape[0]  # n 表示样本个数
    for i in range(n):
        subs = centroids - X[i, :]
        dimension2 = np.power(subs, 2)
        w_dimension2 = np.multiply(w, dimension2)
        w_distance2 = np.sum(w_dimension2, axis=1)
        if math.isnan(w_distance2.sum()) or math.isinf(w_distance2.sum()):
            w_distance2 = np.zeros(K)
            # print 'the situation that w_distance2 is nan or inf'
        idx[i] = np.where(w_distance2 == w_distance2.min())[0][0]
    return idx


def computeCentroids(X, idx, K):
    n, m = X.shape
    centriod = np.zeros((K, m), dtype=float)
    for k in range(K):
        index = np.where(idx == k)[0]  # 一个簇一个簇的分开来计算
        temp = X[index, :]  # ? by m # 每次先取出一个簇中的所有样本
        s = np.sum(temp, axis=0)
        centriod[k, :] = s / np.size(index)
    return centriod


def computeWeight(X, centroid, idx, K, belta):
    n, m = X.shape
    weight = np.zeros((1, m), dtype=float)
    D = np.zeros((1, m), dtype=float)
    for k in range(K):
        index = np.where(idx == k)[0]
        temp = X[index, :]  # 取第k个簇的所有样本
        distance2 = np.power((temp - centroid[k, :]), 2)  # ? by m
        D = D + np.sum(distance2, axis=0)
    e = 1 / float(belta - 1)
    for j in range(m):
        temp = D[0][j] / D[0]
        weight[0][j] = 1 / np.sum((np.power(temp, e)), axis=0)
    return weight


def costFunction(X, K, centroids, idx, w, belta):
    n, m = X.shape
    D = np.zeros((1, m), dtype=float)
    for k in range(K):
        index = np.where(idx == k)[0]
        temp = X[index, :]
        distance2 = np.power((temp - centroids[k, :]), 2)  # ? by m
        D = D + np.sum(distance2, axis=0)
    cost = np.sum(w ** belta * D)
    return cost


def isConvergence(costF, max_iter):
    if math.isnan(np.sum(costF)):
        return False
    index = np.size(costF)
    for i in range(index - 1):
        if costF[i] < costF[i + 1]:
            return False
    if index >= max_iter:
        return True
    elif costF[index - 1] == costF[index - 2] == costF[index - 3]:
        return True
    return 'continue'


def wkmeans(X, K, belta, max_iter):
    n, m = X.shape
    costF = []
    r = np.random.rand(1, m)
    w = np.divide(r, r.sum())
    centroids = InitCentroids(X, K)
    for i in range(max_iter):
        idx = findClosestCentroids(X, w, centroids)
        centroids = computeCentroids(X, idx, K)
        w = computeWeight(X, centroids, idx, K, belta)
        c = costFunction(X, K, centroids, idx, w, belta)
        costF.append(round(c, 4))
        if i < 2:
            continue
        flag = isConvergence(costF, max_iter)
        if flag == 'continue':
            continue
        elif flag:
            best_labels = idx
            best_centers = centroids
            isConverge = True
            return isConverge, best_labels, best_centers, costF
        else:
            isConverge = False
            return isConverge, None, None, costF


class WKMeans:

    def __init__(self, n_clusters=3, max_iter=20, belta=7.0):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.belta = belta

    def fit(self, X):
        self.isConverge, self.best_labels, self.best_centers, self.cost = wkmeans(
            X=X, K=self.n_clusters, max_iter=self.max_iter, belta=self.belta
        )
        return self

    def fit_predict(self, X, y=None):
        if self.fit(X).isConverge:
            return self.best_labels
        else:
            return 'Not convergence with current parameter ' \
                   'or centroids,Please try again'

    def get_params(self):
        return self.isConverge, self.n_clusters, self.belta, 'WKME'

    def get_cost(self):
        return self.cost


def load_data():
    data = load_iris()
    x, y = data.data, data.target
    return x, y


if __name__ == '__main__':
    from sklearn.cluster import KMeans
    x, y = load_data()

    model = KMeans(n_clusters=3)
    model.fit(x)
    y_pred = model.predict(x)
    nmi = normalized_mutual_info_score(y, y_pred)
    print("NMI by sklearn: ", nmi)

    model = WKMeans(n_clusters=3, belta=3)
    while True:
        y_pred = model.fit_predict(x)
        if model.isConverge == True:
            nmi = normalized_mutual_info_score(y, y_pred)
            print("NMI by wkmeans: ", nmi)
            break

# result:
# NMI by sklearn:  0.7581756800057784
# NMI by wkmeans:  0.8130427037493443
