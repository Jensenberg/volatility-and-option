# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 19:42:39 2018

@author: 54326
"""

from math import log, exp, sqrt
from scipy.stats import norm
from scipy.optimize import fsolve

class IV():
    '''定义一个通过Balck-Scholes公式求隐含波动率的类'''    
    Y_days = 365 #一年的总天数，按自然日计算
    
    def __init__(self, S, K, r, T_days, price):
        self.S = S #标的价格
        self.K = K #执行价格
        self.r = r #无风险利率
        self.T = T_days / self.Y_days #到期期限
        self.price = price #期权的交易价格
        
    def bs_value(self, sigma):
        '''
        计算期权的B-S价格
        sigma:
            波动率
        '''
        d1 = (log(self.S / self.K) + (self.r + 0.5 * sigma**2) * self.T)\
             / (sigma * sqrt(self.T))
        d2 = d1 - sigma * sqrt(self.T)
        return self.S * norm.cdf(d1) - self.K * norm.cdf(d2) * exp(-self.r * self.T)
    
    def vega(self, sigma):
        '''
        B-S公式得到的期权价格关于波动率的导数，希腊值vega
        '''
        d1 = (log(self.S / self.K) + (self.r + 0.5 * sigma**2) * self.T)\
             / (sigma * sqrt(self.T))
        return self.S * norm.pdf(d1) * sqrt(self.T)
    
    def newton(self, sigma=0.3, N=50):
        '''
        用牛顿迭代法（Newton-Raphson方法）不断迭代来逼近隐含波动率
        Newton法较稳定，但有时得不到解，尤其是在put价格很小的时候
        N:
            迭代次数
        '''
        for i in range(N):
            sigma -= (self.bs_value(sigma) - self.price) / self.vega(sigma)
        return sigma
    
    def equation(self, sigma):
        '''
        建立一个期权价格与B-S公式得到的理论价格之间的方程
        '''
        return self.bs_value(sigma) - self.price
    
    def solve(self, sigma=0.5):
        '''
        使用scipy.optimize.fsolve求解隐含波动率
        fsovle总能得到解，但有些解有点奇怪，速度比Newton法快一些
        '''
        return fsolve(self.equation, sigma)[0]
            
if __name__ == '__main__':
    from collections import defaultdict
    from itertools import product
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    with pd.HDFStore('E:/data/market.h5') as store: 
        data = store['50ETF_option_VIX']
        shibor = store['shibor_3M']
    close = pd.read_excel('E:/Data/50ETF基金净值表现日数据.xlsx', parse_date=True)
    close['date'] = pd.to_datetime(close['date'])
    close = close.loc[:, ['date', 'close']] #以交易的收盘价作为标的价格
    data = pd.merge(data, shibor, on='date', how='left')
    data = pd.merge(data, close, on='date', how='left')
    data.set_index(['date', 'expire'], inplace=True)
    
    #计算虚值期权的虚值程度，将负虚值设为期权收盘价，以便后面计算最小的虚值程度
    data['k_close'] = np.where(data['strike'] - data['close'] > 0, 
                               data['strike'] - data['close'], data['strike'])
    #计算实值期权的实值程度，将负实值设为期权执行价，以便后面计算最小的实值程度
    data['close_k'] = np.where(data['close'] - data['strike'] > 0, 
                               data['close'] - data['strike'], data['close'])
    otm = data.groupby(level=['date', 'expire'])[['k_close']].min() #最小的虚值
    otm.rename(columns={'k_close': 'otm'}, inplace=True) #otm: out-of-money
    itm = data.groupby(level=['date', 'expire'])[['close_k']].min() #最小的实值
    itm.rename(columns={'close_k': 'itm'}, inplace=True) #itm: in-the-money
    data = data.join(otm)
    data = data.join(itm)
    itm_sp = data[data['itm'] == data['close']] #部分日期没有实值的期权
    #将没有实值期权的实值程度将入一点常量，否则后面会导致所有期权都会入选为最接近执行价的期权
    data['itm'] = np.where(data['itm'] == data['close'], 
                           data['itm'] + 1, data['itm'])
    
    def data_slice(data, value_flag, last_flag):
        '''
        提取最靠近执行价格的期权的数据
        Args:
            data:
                所有交易所有数据
            value_flag:
                实值、虚值标记，值为'otm'或'itm'
            last_flag:
                近月、次近月标志，值为'last'或'last2'
        Returns:
            满足某一实虚值标记，某一次近月标记的所有交易日的数据
        '''
        if value_flag == 'otm':
            spread = 'k_close'
        elif value_flag == 'itm':
            spread = 'close_k'
        else:
            print("value_flag should be 'otm' or 'itm'")
        data_flag = data[(data[spread] == data[value_flag])
                       & (data['T_days'] == data[last_flag])]
        data_flag.reset_index(level=1, inplace=True)
        return data_flag

    def get_iv(data, kind, method='newton'):
        '''
        计算隐含波动率
        data:
            某一交易日，某一实虚值标记，某一次近月标记的数据
        kind:
            看涨期权还是看跌期权，值为'call'或'put'
        method:
            指定计算采用的方法
            Newton法较稳定，但有时得不到解，fsovle总能得到解，但有些解有点奇怪
        '''
        S = data['close']
        K = data['strike']
        r = data['shibor_3M']
        T_days = data['T_days']
        price = data[kind] 
        iv = IV(S, K, r, T_days, price) #返回一个IV类的实例
        if method == 'newton':
            return iv.newton()
        elif method == 'fsolve':
            return iv.solve()
        else:
            print("method should be 'newton' or 'fsolve'")
    
    IVs = {} #保存所有计算到的隐含波动率
    value_flags = ['otm', 'itm']
    last_flags = ['last1', 'last2']
    flags = list(product(value_flags, last_flags)) #value_flags与last_flags的笛卡尔积
    for flag in flags:
        vf, lf = flag
        data_flag = data_slice(data, vf, lf) #提取满足某一实虚值标记，某一次近月标记的数据
        dates = data_flag.index 
        IVs[(vf, lf)] = defaultdict(dict)
        for date in dates:
            data_t = data_flag.loc[date, :]
            method = 'newton' if vf == 'otm' else 'fsolve' #对实值put用fsolve
            IVs[(vf, lf)][date].update({'call': get_iv(data_t, 'call')})
            IVs[(vf, lf)][date].update({'put': get_iv(data_t, 'put', method)})
    
    def call_put_mean(flag):
        return pd.DataFrame(IVs[flag]).T.mean(axis=1) #call和put的平均

    CP_mean = {}
    for flag in flags:
        CP_mean[flag] = call_put_mean(flag)
    CP_mean = pd.DataFrame(CP_mean)
    
    K_spread = {} #提取所有交易日最小的实值程度、虚值程度数据
    for vf in value_flags: #在同一天，不同到期日，最小实值程度、虚值程度是一样的
        data_flag = data_slice(data, vf, 'last1') # 所以last_flag='last2'结果一样
        K_spread[vf] = data_flag[vf]
    K_spread = pd.DataFrame(K_spread)
    #计算基于实值程度、实值程度加权的权数
    K_spread['otm_weight'] = K_spread['itm'] / (K_spread['otm'] + K_spread['itm'])
    K_spread['itm_weight'] = K_spread['otm'] / (K_spread['otm'] + K_spread['itm'])
    
    K_weighted = CP_mean.join(K_spread)
    #通过对最接近平价的最小实值、虚值的期权的波动率按实虚值程度加权，得到近月、次近月波动率
    K_weighted['vol_last1'] = K_weighted[('otm', 'last1')] * K_weighted['otm_weight']\
                            + K_weighted[('itm', 'last1')] * K_weighted['itm_weight']
    K_weighted['vol_last2'] = K_weighted[('otm', 'last2')] * K_weighted['otm_weight']\
                            + K_weighted[('itm', 'last2')] * K_weighted['itm_weight']        
    T_spread = {} #提取所有交易日近月、次近月的剩余到期天数数据
    for lf in last_flags:
        data_flag = data_slice(data, 'otm', lf)
        T_spread[lf] = data_flag['T_days']   
    T_spread = pd.DataFrame(T_spread)
    
    T_weighted = K_weighted.join(T_spread)
    #按剩余期限加权
    T_weighted['last1_weight'] = (T_weighted['last2'] - 30)\
                               / (T_weighted['last2'] - T_weighted['last1'])
    T_weighted['last2_weight'] = (30 - T_weighted['last1'])\
                               / (T_weighted['last2'] - T_weighted['last1'])
    T_weighted['VIX'] = T_weighted['vol_last1'] * T_weighted['last1_weight']\
                      + T_weighted['vol_last2'] * T_weighted['last2_weight']
    #对于nan值，用最原始的8个波动率中的可得值的简单平均替代
    nan_dates = T_weighted[T_weighted['VIX'].isnull()].index
    for date in nan_dates:
        T_weighted.loc[date, 'VIX'] = T_weighted.loc[date, flags].mean()
    
    plt.figure(figsize=(15, 8))
    plt.plot(T_weighted['VIX'])
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylabel('VIX', fontsize=16)
    plt.xlabel('date', fontsize=16)
    plt.title('VIX-Whaley', fontsize=16)
    plt.savefig('VIX_old.png', bbox_inches='tight')
