"""
@Time ： 2021-07-07 21:06
@Auth ： DongZhou GU
@File ：gm.py
@IDE ：PyCharm

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox  # 白噪声检验
import statsmodels.tsa.stattools as st
import scipy.stats as scs
from statsmodels.tsa.arima_model import ARIMA


class Arima:
    def __init__(self, data, n):
        """
            :param data: Series/np/list
            :param n: 预测数量
        """
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        if isinstance(data, pd.Series):
            self.data = data.values
        elif isinstance(data, np.ndarray):
            self.data = data
        elif isinstance(data, list):
            self.data = np.array(data)
        self.check()
        self.pre_model()
        self.build_model(n)
        print("返回值为dataframe，可通过.res_df拿到, 可通过.plot_res画预测图\n", self.res_df)

    def check(self):
        series = pd.Series(self.data.reshape(-1))
        # 平稳性ADF检验
        print('+++++++++++++++++++++++++++++++++开始进行平稳性ADF检验+++++++++++++++++++++++++++++++')
        d = 0
        while (True):
            if (d > 0):
                series = series.diff(1)
                series = series.dropna(how=any)
            t = sm.tsa.stattools.adfuller(series, )
            output = pd.DataFrame(
                index=['Test Statistic Value', "p-value", "Lags Used", "Number of Observations Used",
                       "Critical Value(1%)",
                       "Critical Value(5%)", "Critical Value(10%)"], columns=['value'])
            output['value']['Test Statistic Value'] = t[0]
            output['value']['p-value'] = t[1]
            output['value']['Lags Used'] = t[2]
            output['value']['Number of Observations Used'] = t[3]
            output['value']['Critical Value(1%)'] = t[4]['1%']
            output['value']['Critical Value(5%)'] = t[4]['5%']
            output['value']['Critical Value(10%)'] = t[4]['10%']
            print(output)
            if t[1] > 0.05:
                print(f'单位根检验中p值为{t[1]}，大于0.05，为非平稳序列,进行{d + 1}阶差分')
                d += 1
            else:
                print('单位根检验中p值为%.2f，小于0.05，为平稳序列' % (t[1]))
                self.d = d
                break
        print(f'++++++++++++++++++++++++++ADF检验完成，{d}阶差分后已为平稳序列+++++++++++++++++++++++++++++++')
        print(f'++++++++++++++++++++++++++开始白噪声检验+++++++++++++++++++++++++++++++')
        noiseP = acorr_ljungbox(series, lags=1)[-1]
        if noiseP <= 0.05:
            print('白噪声检验中p值为%.2f，小于0.05，为非白噪声' % noiseP)
        else:
            print('白噪声检验中%.2f，大于0.05，为白噪声' % noiseP)
        print(f'++++++++++++++++++++++++++白噪声检验完成+++++++++++++++++++++++++++++++')
        self.data_diff = series

    def pre_model(self):
        series = self.data_diff
        self.time_plot(series)
        import warnings
        warnings.filterwarnings("ignore")
        pMax = int(series.shape[0] / 10)  # 一般阶数不超过length/10
        qMax = pMax  # 一般阶数不超过length/10
        order = st.arma_order_select_ic(series, max_ar=pMax, max_ma=qMax, ic=['aic', 'bic', 'hqic'])
        p, q = order.aic_min_order
        print('AIC准则下确定p,q为%s,%s' % (p, q))
        p, q = order.bic_min_order
        print('BIC准则下确定p,q为%s,%s' % (p, q))
        self.q = q
        self.p = p

    # 借助AIC、BIC统计量自动确定p,q
    def build_model(self, n):
        print(f'++++++++++++++++++++++++++开始建立ARIMA模型+++++++++++++++++++++++++++++++')
        series = pd.Series(self.data.reshape(-1))
        print('ARIMA建模使用参数：p=%s,d=%s,q=%s' % (self.p, self.d, self.q))
        model = ARIMA(series, order=(self.p, self.d, self.q)).fit()
        predict_n = model.forecast(n)[0]
        print(model.summary())

        fit_v = model.fittedvalues
        for _ in range(self.d):
            fit_v = fit_v.cumsum()
        fit_v += series[0]
        fit_res = [series[0]]
        fit_res.extend(x for x in fit_v)
        fit_res.extend(x for x in predict_n)

        delta = [np.nan]
        delta.extend(x for x in model.resid)
        self.res_df = pd.concat([pd.DataFrame({'原始值': self.data}), pd.DataFrame({'预测值': fit_res}),
                                 pd.DataFrame({'残差': delta}),
                                 pd.DataFrame(
                                     {'相对误差': list(map(lambda x: '{:.2%}'.format(x), np.abs(delta / self.data)))})
                                 ], axis=1)
        self.verify(model.resid)

    # 模型验证，针对残差
    def verify(self, resid):
        print(f'++++++++++++++++++++++++++开始模型验证+++++++++++++++++++++++++++++++')
        t = sm.tsa.stattools.adfuller(resid, )
        output = pd.DataFrame(
            index=['Test Statistic Value', "p-value", "Lags Used", "Number of Observations Used",
                   "Critical Value(1%)",
                   "Critical Value(5%)", "Critical Value(10%)"], columns=['value'])
        output['value']['Test Statistic Value'] = t[0]
        output['value']['p-value'] = t[1]
        output['value']['Lags Used'] = t[2]
        output['value']['Number of Observations Used'] = t[3]
        output['value']['Critical Value(1%)'] = t[4]['1%']
        output['value']['Critical Value(5%)'] = t[4]['5%']
        output['value']['Critical Value(10%)'] = t[4]['10%']
        print(output)
        resid = pd.Series(resid)
        self.time_plot(resid, title='ARIMA残差')

    def time_plot(self, series, title=''):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        fig = plt.figure(figsize=(10, 8))
        layout = (3, 2)
        ts_ax = plt.subplot2grid(layout, (0, 0), colspan=2)
        acf_ax = plt.subplot2grid(layout, (1, 0))
        pacf_ax = plt.subplot2grid(layout, (1, 1))
        qq_ax = plt.subplot2grid(layout, (2, 0))
        pp_ax = plt.subplot2grid(layout, (2, 1))
        series.plot(ax=ts_ax)
        ts_ax.set_title(f'{title}时序图')
        plot_acf(series, ax=acf_ax, alpha=0.5)
        acf_ax.set_title('自相关系数')
        plot_pacf(series.values, ax=pacf_ax, nlags=series.shape[0] - 2, alpha=0.5)
        pacf_ax.set_title('偏自相关系数')
        sm.qqplot(series, line='s', ax=qq_ax)
        qq_ax.set_title('QQ 图')
        scs.probplot(series, sparams=(series.mean(),
                                      series.std()), plot=pp_ax)
        pp_ax.set_title('PP 图')
        plt.tight_layout()
        plt.show()

    def plot_res(self, xlabel='', ylabel=''):
        res_df = self.res_df
        f, ax = plt.subplots(figsize=(8, 5))
        sns.lineplot(x=res_df.index.tolist(), y=res_df['预测值'], linewidth=2, ax=ax)
        sns.scatterplot(x=res_df.index.tolist(), y=res_df['原始值'], s=60, color='r', marker='v', ax=ax)
        plt.fill_between(np.where(np.isnan(res_df["原始值"]))[0], y1=min(plt.yticks()[0]), y2=max(plt.yticks()[0]),
                         color='orange', alpha=0.2)
        ax.set_xlabel(xlabel, fontsize=15)
        ax.set_ylabel(ylabel, fontsize=15)
        plt.show()


if __name__ == "__main__":
    data = np.array([1.2, 2.2, 3.1, 4.5, 5.6, 6.7, 7.1, 8.2, 9.6, 10.6, 11, 12.4, 13.5, 14.7, 15.2])
    x = data[0:10]  # 输入数据
    arima = Arima(x, 5)  # 预测后面5个数据
    res_df = arima.res_df
    arima.plot_res()
