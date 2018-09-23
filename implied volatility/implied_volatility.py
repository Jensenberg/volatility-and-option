# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 16:12:39 2018

@author: 54326
"""

from math import exp, log, sqrt
from scipy.stats import norm
from collections import defaultdict
from scipy.optimize import brentq
#from scipy.optimize import fsolve

def bs_value(S0, K, r, sigma, T):
    '''
    计算欧式看涨期权的价格
    Parameters:
        S0:
            期初价格
        K:
            执行价格
        r:
            无风险利率
        sigma:
            波动率
        T:
            期权的期限，以年为单位
    Returns:
        期权的B-S价格            
    '''
    d1 = (log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    return S0 * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)           

def bs_vega(S0, K, r, sigma, T):
    '''
    计算期权的vega
    '''
    d1 = (log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    return S0 * norm.pdf(d1) * sqrt(T)

def pseudo_mc(close, n, M=1200):
    '''
    将一定期限的收盘价序列依次向后滚动，得到M个期权的价格序列，视为蒙特卡洛模拟的路径，
    计算M个期权到期后损益的期望，即平均值
    Parameters:
        close:
            收盘价
        n:
            期权的期限，以天为单位
        M:
            模拟的路径数
    Returns:
        M个期权的损益的平均值
    '''
    PL = (close[n + i] / close[i] - 1 for i in range(M)
          if close[n + i] > close[i])
    return sum(PL) / M       

def implied(close, r, sigma=0.5, S0=1, K=1, T=0.25, days=240, M=1200, N=50):
    '''
    利用牛顿迭代法求解期限为3个月的平价欧式看涨期权的隐含波动率
    Parameters:
        days:
            一年的交易天数
        N:
            迭代次数，N在20~100时，费时2-3分钟
    '''
    n = int(T * days)
    price = pseudo_mc(close, n, M) / (1 + r * T)
    for i in range(N):
        value = bs_value(S0, K, r, sigma, T)
        vega = bs_vega(S0, K, r, sigma, T)
        sigma -= (value - price) / vega
    return sigma
    
def rolling_implied(close, shibor, sigma=0.5, S0=1, K=1, T=0.25, days=240, 
                    M=1200, N=50):
    '''
    计算隐含波动率序列
    Parameters:
        shibor:
            期限为T的Shibor，作为无风险利率
    Returns: 
        iv:
            dict, 日期为键，波动率为值
    '''
    C = len(close)
    n = int(T * days)
    iv = {}
    for i in range(C - M - n):
        close_i = close[i: M + n + i]
        date = close_i.index[0]
        try:
            r = shibor[date]
        except:
            r = 0.03
        iv[date] = implied(close_i, r, sigma, S0, K, T, days, M, N)
    return iv
    
def hedge_cost(close, r, sigma, T=0.25, days=240):
    '''
    计算delta-中性对冲后的损益
    '''
    n = int(T * days)
    S0 = K = close[0]
    d1_0 = (log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    delta_0 = norm.cdf(d1_0)
    cash_0 = S0 * delta_0 * (1 + r / days)
    d = defaultdict(list)
    d['delta'].append(delta_0); d['cash'].append(cash_0)
    for i in range(1, n + 1):
        T_i = T - i / days
        if T_i == 0: # 期权到期时， T_i=0，进行特别处理以避免出现ZeroDivisionErro
            delta_i = 1 if close[n] > K else 0 
        else:
            d1_i = (log(close[i] / K) + (r + 0.5 * sigma**2) * T_i)\
                 / (sigma * sqrt(T_i))
            delta_i = norm.cdf(d1_i)
        trade_i = delta_i - d['delta'][i-1]
        cash_i = (d['cash'][i -1] + trade_i * close[i]) * (1 + r / days)
        d['delta'].append(delta_i); d['cash'].append(cash_i)        
    pl = d['cash'][n] - K if close[n] > K else d['cash'][n]
    return pl / (1 + r * T)

def equation(sigma, close=None, shibor=None, T=0.25):
    '''
    建立以sigma为未知数的对冲成本与期权价格的方程
    value(sigma) - price(sigma) = 0
    '''
    S0 = K = close[0]
    date = close.index[0]
    try:
        r = shibor[date]
    except:
        r = 0.03
    value = bs_value(S0, K, T, r, sigma)
    price = hedge_cost(close, r, sigma)
    return value - price

def solve(func, close, shibor):
    '''
    求解满足方程equation的sigma
    brentq方法耗时1分钟左右，fsolve耗时2分钟左右
    Parameters:
        func:
            方程
    Returns:
        对冲隐含波动率
    '''
#    return fsolve(func, 0.3, args=(close, shibor))[0]
    return brentq(func, 0.05, 1, args=(close, shibor))

def rolling_hedge(close, shibor, T=0.25, days=240):
    '''
    返回对冲隐含波动率序列
    '''
    C = len(close)
    n = int(T * days)
    iv= {}
    for i in range(C - n - 1):
        close_i = close[i: n + i + 1]
        date = close_i.index[0]
        iv[date] = solve(equation, close_i, shibor)
    return iv    

if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt
    
    zz500 = pd.read_excel('e:/alpha/zz500.xlsx')
    zz500.set_index(pd.to_datetime(zz500['date']), inplace=True)
    shibor = pd.read_excel('E:/Alpha/shibor_3M.xlsx', index_col='date')

    close = zz500['close']
    # 以第一种方法计算的隐含波动率
    # 在rolling_implied函数中设置M=600, 1200, 2000可以得到大不相同的结果
    iv_600 = pd.Series(rolling_implied(close, shibor, M=600))
    iv_1200 = pd.Series(rolling_implied(close, shibor, M=1200))
    iv_2000 = pd.Series(rolling_implied(close, shibor, M=2000))
    iv = pd.concat([iv_600, iv_1200, iv_2000], axis=1)
    iv.columns = ['iv(M=600)', 'iv(M=1200)', 'iv(M=2000)']
    plt.figure()
    iv.plot(figsize=(15, 8), fontsize=14)
    plt.xticks(rotation=0)
    plt.title('Implied Volatility, zz500', fontsize=16)
    plt.legend(fontsize='14')
    plt.savefig('implied volatility.png', bbox_inches='tight')
    
    # 在rolling_hedge中设置N=20, 50, 100，耗时和得到的结果均只是略有差异
    iv_hedge = pd.Series(rolling_hedge(close, shibor)) # 对冲隐含波动率
    plt.figure()
    iv_hedge.plot(figsize=(15, 8), fontsize=14)
    plt.title('Hedged Implied Volatility', fontsize=16)
    plt.xticks(rotation=0)
    plt.savefig('hedged implied volatility.png', bbox_inches='tight')
