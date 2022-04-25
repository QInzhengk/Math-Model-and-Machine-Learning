"""
@Time ： 2021-07-10 21:52
@Auth ： DongZhou GU
@File ：AHP.py
@IDE ：PyCharm

"""
import numpy as np
import pandas as pd
import warnings


class AHP:
    def __init__(self, criteria, b):
        self.RI = (0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49)
        self.criteria = criteria
        self.b = b
        self.num_criteria = criteria.shape[0]
        self.num_project = b[0].shape[0]

    def cal_weights(self, input_matrix):
        input_matrix = np.array(input_matrix)
        n, n1 = input_matrix.shape
        assert n == n1, '不是一个方阵'
        for i in range(n):
            for j in range(n):
                if np.abs(input_matrix[i, j] * input_matrix[j, i] - 1) > 1e-7:
                    raise ValueError('不是反互对称矩阵')

        eigenvalues, eigenvectors = np.linalg.eig(input_matrix)

        max_idx = np.argmax(eigenvalues)
        max_eigen = eigenvalues[max_idx].real
        eigen = eigenvectors[:, max_idx].real
        eigen = eigen / eigen.sum()

        if n > 9:
            CR = None
            warnings.warn('无法判断一致性')
        else:
            CI = (max_eigen - n) / (n - 1)
            CR = CI / self.RI[n]
        return max_eigen, CR, eigen

    def run(self):
        max_eigen, CR, criteria_eigen = self.cal_weights(self.criteria)
        print('准则层：最大特征值{:<5f},CR={:<5f},检验{}通过'.format(max_eigen, CR, '' if CR < 0.1 else '不'))
        print('准则层权重={}\n'.format(criteria_eigen))

        max_eigen_list, CR_list, eigen_list = [], [], []
        for i in self.b:
            max_eigen, CR, eigen = self.cal_weights(i)
            max_eigen_list.append(max_eigen)
            CR_list.append(CR)
            eigen_list.append(eigen)

        pd_print = pd.DataFrame(eigen_list,
                                index=['准则' + str(i) for i in range(self.num_criteria)],
                                columns=['方案' + str(i) for i in range(self.num_project)],
                                )
        pd_print.loc[:, '最大特征值'] = max_eigen_list
        pd_print.loc[:, 'CR'] = CR_list
        pd_print.loc[:, '一致性检验'] = pd_print.loc[:, 'CR'] < 0.1
        print('方案层')
        print(pd_print)

        # 目标层
        obj = np.dot(criteria_eigen.reshape(1, -1), np.array(eigen_list))
        print('\n目标层', obj)
        print('最优选择是方案{}'.format(np.argmax(obj)))
        return obj


if __name__ == '__main__':
    # 准则重要性矩阵
    criteria = np.array([[1, 2, 7, 5, 5],
                         [1 / 2, 1, 4, 3, 3],
                         [1 / 7, 1 / 4, 1, 1 / 2, 1 / 3],
                         [1 / 5, 1 / 3, 2, 1, 1],
                         [1 / 5, 1 / 3, 3, 1, 1]])

    # 对每个准则，方案优劣排序
    b1 = np.array([[1, 1 / 3, 1 / 8], [3, 1, 1 / 3], [8, 3, 1]])
    b2 = np.array([[1, 2, 5], [1 / 2, 1, 2], [1 / 5, 1 / 2, 1]])
    b3 = np.array([[1, 1, 3], [1, 1, 3], [1 / 3, 1 / 3, 1]])
    b4 = np.array([[1, 3, 4], [1 / 3, 1, 1], [1 / 4, 1, 1]])
    b5 = np.array([[1, 4, 1 / 2], [1 / 4, 1, 1 / 4], [2, 4, 1]])

    b = [b1, b2, b3, b4, b5]
    a = AHP(criteria, b).run()
