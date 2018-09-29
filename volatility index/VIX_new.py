# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 20:33:38 2018

@author: 54326
"""

from math import exp, sqrt

class Vix():
    '''
    定义一个用方差互换和波动率互换方法编制VIX指数的类，基于50ETF期权
    '''    
    def __init__(self, T_days, strikes, calls, puts, r):
        '''
        T_days:
            剩余到期天数
        strikes:
            当日可交易期权的执行价序列
        calls:
            看涨期权的价格序列
        puts:
            看跌期权的价格序列
        r:
            无风险利率，以3个月的Shibor为基准
        '''
        self.T_days = T_days
        self.strikes = strikes
        self.calls = calls
        self.puts = puts
        self.r = r
        
    def T(self, Y_days=365):
        '''
        计算剩余期限按年计算的比例
        Y_days:
            一年的总天数
        '''
        return self.T_days / Y_days
    
    def F(self):
        '''
        看涨期权和看跌期权价差绝对值最小对应的执行价格的远期价格
        '''
        C_P = abs(self.calls - self.puts)
        K_F = C_P.idxmin()
        return K_F + (self.calls[K_F] - self.puts[K_F]) * exp(self.r * self.T())
    
    def Ks(self):
        '''
        将执行价格从小到大排序，并返回列表
        '''
        ks = list(self.strikes)
        ks.sort()
        return ks
    
    def K0(self):
        '''
        低于F值的第一个执行价格为K0
        '''
        ks = self.Ks()
        K_F = self.F()
        i = 0
        while ks[i] < K_F:
            i += 1
        return ks[i-1]
    
    def delta_K(self):
        '''
        执行价格的价差为相邻价格差的均值，[K(i+1) - K(i-1)] / 2
        特别地，最低执行价格的价差为K2 - K1，最高执行价格价差为K(N-1) - K(N-2)
        '''
        delta_k = {}
        ks = self.Ks()
        delta_k[ks[0]] = ks[1] - ks[0]
        delta_k[ks[-1]] = ks[-1] - ks[-2]
        for i in range(1, len(ks) - 1):
            delta_k[ks[i]] = (ks[i+1] - ks[i-1]) / 2
        return delta_k
    
    def Q_K(self):
        '''
        期权费用，按结算价计算
        K < K0，为看跌期权价格，K > K0，为看涨期权价格，K = K0时是看涨和看跌期权价格的均值
        由于期权价格均大于0，无需考虑期权费为0的情况
        '''
        q_k = {}
        k0 = self.K0()
        for k in self.Ks():
            if k < k0:
                q_k[k] = self.puts[k]
            elif k > k0:
                q_k[k] = self.calls[k]
            else:
                q_k[k] = (self.calls[k] + self.puts[k]) / 2
        return q_k

    def sigma2(self):
        '''
        计算某一个时刻，某一到期期限的波动率
        '''
        delta_k = self.delta_K()
        q_k = self.Q_K()
        T = self.T()
        ks = self.Ks()
        sum_K = sum(delta_k[k] / k**2 * q_k[k] * exp(self.r * T)
                    for k in ks)
        return 2*sum_K / T - (self.F()/self.K0() - 1) ** 2 / T
    
    def volatility(self, other, M_days=30, Y_days=365):
        '''
        将近月和次近月期权的波动率加权，得到对未来30天的波动率的预期值
        M_days:
            一个月的总天数
        Y_days:
            一年的总天数
        '''
        last1 = self.sigma2() * self.T() * (other.T_days - M_days)\
                / (other.T_days - self.T_days)
        last2 = other.sigma2() * other.T() * (M_days - self.T_days)\
                / (other.T_days - self.T_days)
        return 100 * sqrt((last1 + last2)  * Y_days / M_days)

if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt
    
    with pd.HDFStore('E:/data/market.h5') as store: 
        data = store['50ETF_option_VIX']
        shibor = store['shibor_3M']
    data.set_index(['date', 'expire'], drop=False, inplace=True)
    dates = data['date'].drop_duplicates() 
    
    def data_slice(data, last_flag):
        '''
        提取近月或次近月的期权数据
        Args:
            data:
                某一个交易的所有期权的数据
            last_flag:
                近月或次近月的标志，为’last1'或'last2'
        Returns:
            执行价格序列，看涨期权价格序列，看跌期权价格序列
        '''
        data_last = data[data['T_days'] == data[last_flag]]
        data_last.set_index('strike', drop=False, inplace=True)
        return data_last['strike'], data_last['call'], data_last['put']
    
    def vix(T_days, data, last_flag, r):
        '''
        返回一个Vix实例
        '''
        strikes, calls, puts = data_slice(data, last_flag) 
        return Vix(T_days, strikes, calls, puts, r)
    
    VIX = {} #将得到的volatility值，以日期为键，保存到字典VIX
    for date in dates:
        r = shibor.loc[date, 'shibor_3M']
        data_t = data.xs(date, level=0) #某一交易日的数据
        T_days_1 = data_t['last1'][0] #近月的剩余到期天数
        T_days_2 = data_t['last2'][0] #次近月的剩余到期天数
        vix_1 =  vix(T_days_1, data_t, 'last1', r)
        vix_2 =  vix(T_days_2, data_t, 'last2', r)
        VIX[date] = vix_1.volatility(vix_2) 
    
    VIX = pd.Series(VIX).sort_index()
    plt.figure(figsize=(15, 8))
    plt.plot(VIX)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlabel('date', fontsize=16)
    max_index = VIX.idxmax().strftime('%Y/%m/%d')
    max_value = VIX.max()
    plt.annotate('%s VIX=%.2f, ' %(max_index, max_value) 
                +'rise margin ratio from 12% to 20%', 
                 xy=(max_index, VIX[max_index]),
                 xytext=(50, 0),
                 textcoords='offset points',
                 arrowprops=dict(arrowstyle="->"),
                 fontsize=16)
    plt.ylabel('VIX', fontsize=16)
    plt.title('VIX-Demeterfi', fontsize=16)
    plt.savefig('VIX_new.png',bbox_inches='tight')    
