import copy
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import cross_validate, train_test_split
from torch.utils.data import DataLoader, Dataset
from torch import optim


class myDataset(Dataset):
    """"
    X : data
    related:列表的列表 eg:[[1,2],[3,4]]  1和2 是关联事件  3 和 4是关联使事件
    """
    def __init__(self, X, related):
        self.X = X
        self.related = related

    def __getitem__(self, index):

        #  1 ----同类   0 ----异类
        should_get_same_class = random.randint(0, 1)
        if should_get_same_class:
            i = random.randint(0, len(self.related) - 1)
            indexs = random.sample(self.related[i], 2)
            index1 = indexs[0]
            index2 = indexs[1]
        else:
            indexs = random.sample(range(0, len(self.related)), 2)
            index1 = random.sample(self.related[indexs[0]], 1)[0]
            index2 = random.sample(self.related[indexs[1]], 1)[0]

        label = should_get_same_class
        #         print(index1)
        #         print(index2)
        #         print(label)
        return self.X[index1, :], self.X[index2, :], label

    def __len__(self):
        # return self.dataset_X.size()[0]
        return 100


class logistic_similiar(nn.Module):
    """
    使用方式 ：  ls = logistic_similiar(5)
                criterion = nn.BCELoss()  # 定义损失函数
                optimizer = optim.Adam(ls.parameters(), lr=0.001,weight_decay=0.001)
                ls.fit(X,related,100,optimizer,criterion,500)
                print(ls.prefict(X[0,:],X[2,:]))

    """
    def __init__(self, in_feature):
        super(logistic_similiar, self).__init__()

        self.to_logistic = nn.Sequential(
            nn.Linear(in_features=in_feature, out_features=1),
            nn.Sigmoid()
        )

        for m in self.modules():
            if isinstance(m, nn.Linear):
                torch.nn.init.xavier_normal_(m.weight, gain=1, )
                torch.nn.init.constant_(m.bias, 0)

    def forward(self, input1, input2):
        input = torch.abs(input1 - input2)
        output = self.to_logistic(input)
        return output

    def fit(self, X, related, batch_size, optimizer, criterion, EPOCH=100):
        self.train()
        X = torch.tensor(X, dtype=torch.float)
        TrainDataSet = myDataset(X, related)
        train_dataloader = DataLoader(dataset=TrainDataSet, shuffle=True, batch_size=10)
        for epoch in range(EPOCH):
            for i, data in enumerate(train_dataloader, 0):
                optimizer.zero_grad()
                input1, input2, label = data
                out = self.forward(input1, input2)
                out = out.squeeze()
                label = label.float()
                loss = criterion(out, label)
                lossval = loss.item()
                loss.backward()
                optimizer.step()

    #             print("Epoch: {:04d}".format(epoch + 1), "loss_train: {:.4f}".format(lossval))

    #### 一个一个数据算的
    def prefict(self, X1, X2):

        self.eval()
        X1 = torch.tensor(X1, dtype=torch.float)
        X2 = torch.tensor(X2, dtype=torch.float)
        simi = self.forward(X1, X2)
        return simi.detach().numpy()[0]