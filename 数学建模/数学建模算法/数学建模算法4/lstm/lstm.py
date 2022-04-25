import torch
from torch.autograd import Variable
import torch.nn as nn
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np

class lstm_reg(nn.Module):
    def __init__(self, input_size, hidden_size, output_size=1, num_layers=2):
        '''
        :param input_size:输入样本的特征维度
        :param hidden_size:LSTM层的神经元个数
        :param output_size:输出的特征维度
        :param num_layers:LSTM网络的层数
        '''
        super(lstm_reg, self).__init__()
        self.rnn = nn.LSTM(input_size, hidden_size, num_layers)#lstm层
        self.reg = nn.Linear(hidden_size, output_size)#线性层

    def forward(self, x):
        x, _ = self.rnn(x)
        s, b, h = x.shape
        x = x.view(s*b, h)
        x = self.reg(x)
        x = x.view(s, b, -1)
        return x

#创建预测输入和输出数据集
def create_dataset(dataset,look_back=2):
    '''
    :param dataset: 数据集
    :param look_back: 滑动窗口大小
    :return: 预测的输入data_X,输出data_Y
    '''
    data_X, data_Y = [], []
    for i in range(len(dataset)-look_back):
        a = dataset[i: i+look_back]
        data_X.append(a)
        data_Y.append(dataset[i+look_back])
    return np.array(data_X), np.array(data_Y)

#划分测试集和训练集，默认分割系数为0.7,然后改变数据集的形状使其符合lstm的输入
def split_reshape_dataset(data_X, data_Y, factor=0.7,look_back=2):
    train_size = int(len(data_X) * factor)
    train_X = data_X[:train_size]
    train_Y = data_Y[:train_size]

    test_X = data_X[train_size:]
    test_Y = data_Y[train_size:]

    #我们需要将数据改变一下形状，因为 lstm 读入的数据维度是 (seq, batch, feature)，
    # 所以要重新改变一下数据的维度，这里只有一个序列，所以 batch 是 1，
    # 而输入的 feature 就是我们希望依据的特征，这里默认的是根据前两天的输入来进行预测（也就是滑动窗口的大小），所以 feature 就是 2.
    train_X = train_X.reshape(-1, 1, look_back)
    train_Y = train_Y.reshape(-1, 1, 1)
    test_X = test_X.reshape(-1, 1, look_back)
    test_Y = test_Y.reshape(-1, 1, 1)

    return train_X, train_Y, test_X, test_Y

#数据预处理
def data_preprocessing(dataset):
    """
    :param dataset: 数据集
    :return: 归一化后的数据，归一化的尺度
    """
    dataset = dataset.dropna()  # 丢弃空值
    if isinstance(dataset, pd.Series):
        data = dataset.values
    elif isinstance(dataset, list):
        data = np.array(dataset)
    elif isinstance(dataset, np.ndarray):
        data = dataset
    else:
        data = dataset.values
    data = data.astype('float32')
    #0-1归一化
    scalar = np.max(data) - np.min(data)
    data = list(map(lambda x: x / scalar, data))
    return data, scalar

if __name__ == "__main__":
    dataset = pd.read_csv('data.csv', usecols=[1])
    data, scalar = data_preprocessing(dataset)
    data_X, data_Y = create_dataset(data)
    train_X, train_Y, test_X, test_Y = split_reshape_dataset(data_X, data_Y)
    #构建lstm网络
    net = lstm_reg(2, 4)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-2)
    #开始训练
    # print("=================开始训练====================")
    # print(train_X)
    # for e in range(10000):
    #     train_X = torch.as_tensor(torch.Tensor(train_X), dtype=torch.float32)
    #     train_Y = torch.as_tensor(torch.Tensor(train_Y), dtype=torch.float32)
    #     out = net.forward(train_X)
    #     loss = criterion(out, train_Y)
    #     optimizer.zero_grad()
    #     loss.backward()
    #     optimizer.step()
    #     if (e+1) % 100 == 0:
    #         print('Epoch: {}, Loss:{:.5f}'.format(e+1, loss.item()))
    # #保存训练好的模型
    # torch.save(net.state_dict(), "data.net_params.pkl")
    #加载模型
    net.load_state_dict(torch.load('data.net_params.pkl'))
    #预测值
    test_X = torch.as_tensor(torch.Tensor(test_X), dtype=torch.float32)
    pred_test = net.forward(test_X)
    # 乘以原来归一化的刻度放缩回到原来的值域
    origin_test_Y = test_Y * scalar
    origin_pred_test = pred_test * scalar
    #画图
    plt.plot(origin_pred_test.data.numpy().reshape(-1), 'r', label='prediction')
    plt.plot(origin_test_Y.reshape(-1), 'b', label='real')
    plt.legend(loc='best')
    plt.show()

    #计算MSE
    true_data = origin_test_Y.data
    true_data = np.array(true_data)
    true_data = np.squeeze(true_data)  # 从二维变成一维
    MSE = true_data - origin_pred_test.data.numpy().reshape(-1)
    MSE = MSE * MSE
    MSE_loss = sum(MSE) / len(MSE)
    print("MSE_loss =",MSE_loss)

