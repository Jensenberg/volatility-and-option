# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 20:47:07 2018

@author: 54326
"""

## 可以先不计算delta，以节约时间

from random import uniform
from math import sqrt, log, cos, pi
from collections import defaultdict
import numpy as np

def std_norm(n):
    '''
    利用Box-Muller转换生成标准正态分布的随机变量
    Args:
        n:
            需要生成的随机数个数
    Returns:
        n个标准正态随机数的列表
    '''
    norm = (sqrt(-2 * log(uniform(0, 1))) * cos(2 * pi * uniform(0, 1)) 
            for i in range(n))
    return list(norm)
    
def mc_paths(S0, sigma, n, r=0.04, M=50000, days=20):
    '''
    以一天为步长，假定价格服从几何布朗运动，生成M条从0时刻到20 * n时刻的价格变化路径
    Args:
        S0:
            期初价格
        sigma:
            波动率
        n:
            期限，以月为单位
        r:
            无风险利率
        M:
            模拟的次数
        days:
            每个月的交易日数
    Returns:
        (n+1) * M的numpy二维数组
    '''
    dt = 1 / (12 * days)
    paths = np.zeros((n*days + 1, M))
    paths[0] = S0
    for i in range(1, n*days + 1):
        paths[i] = paths[i-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma
                                       * sqrt(dt) * np.array(std_norm(M)))
    return paths

def phoenix_pl(path, n, upper, lower, coupon, r=0.04, days=20):
    '''
    计算给定路径下期权期末的损益
    Args:
        path:
            价格路径
        n:
            期限，月份数
        upper:
            向上敲出的价格
        lower:
            向下敲入的价格
        coupon:
            每月息票率
    Returns:
        期权卖方的损益
    '''
    strike_in = [] # 记录是否敲入标记
    for i in range(n):
        prices = path[days*i + 1: days*(i+1) + 1]
        # 在每个月里，只要有一次跌破敲入价格，那么久敲入，strike_in记为True
        strike_in.append(any(price < lower for price in prices))
        if prices[-1] > upper:
            strike_out = True
            break # 如果敲出，则后续的价格变化不用考虑
        else:
            strike_out =False
    # 敲入了看跌期权的月份，不支付利息
    interest = path[0] * coupon * (i+1 - strike_in.count(True))
    # 如果存续期内都没有敲出，则到期时考虑是否敲入了看跌期权
    if strike_out == False and any(strike_in):
        gain = path[0] - path[-1] if path[0] > path[-1] else 0
        return gain - interest
    else:
        return interest

def phoenix_value(paths, n, upper, lower, coupon, r=0.04, days=20):
    '''
    通过取所有路径期末损益的均值，贴现回期初即为期权的价格
    Args:
        paths:
            M条模拟路径
    Returns:
        期权价格
    '''
    M = paths.shape[1]    
    PL = (phoenix_pl(paths[:, i], n, upper, lower, coupon, r, days) 
          for i in range(M))
    return sum(PL) / M / (1 + r * n/12)

def phoenix_delta(paths, n, upper, lower, coupon, r=0.04, days=20, point=0.01):
    '''
    delta = 期权价格变化/标的价格变化
    Args:
        point:
            标的价格变化的百分比，0.01表示变化了1%
    Returns:
        delta的近似值
    '''
    paths_plus = paths * (1 + point) # 所有路径同时变大point
    paths_sub = paths * (1- point) # 所有路径同时变小point
    value_plus = phoenix_value(paths_plus, n, upper, lower, coupon)
    value_sub = phoenix_value(paths_sub, n, upper, lower, coupon) 
    return (value_plus - value_sub) / (paths[0, 0] * point * 2)

def phoenix(S0, sigmas, ns, upper, lower, coupon, r=0.04, M=50000, days=20):
    '''
    计算不同波动率，不同到期期限的凤凰期权的价格和delta
    Args:
        sigmas:
            波动率序列
        ns:
            期限序列
    Returns:
        两个字典构成的元组，字典以波动率、期限为键，值分别为价格和delta值
    '''
    values = defaultdict(dict)
    deltas = defaultdict(dict)
    for n in ns:
        for sigma in sigmas:
            paths = mc_paths(S0, sigma, n, r, M, days)
            values[n].update({sigma: phoenix_value(paths, n, upper, lower, coupon)})
            deltas[n].update({sigma: phoenix_delta(paths, n, upper, lower, coupon)})
    return values, deltas
    
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import pandas as pd
    
    # 期初价格为100，波动率为0.3，期限为3个月，无风险利率为0.04，产生10000条路径
    paths = mc_paths(100, 0.3, 3, 0.04, 50000)
    # 计算敲出价格为101，敲入价格为85，月息票率为1.5%时的第一条路径的损益
    print('第一条路径的期末损益：', phoenix_pl(paths[:, 0], 3, 101, 85, 0.015))
    
    plt.figure(figsize=(15, 6))
    plt.plot(paths[:, 0])
    plt.xlabel('day', fontsize=14)
    plt.ylabel('price', fontsize=14)
    plt.xlim(0, 64)
    plt.hlines(101, 0, 62, 'b', '--')
    plt.hlines(85, 0, 62, 'b', '--')
    y_min = min(paths[:, 0].min() - 1, 84)
    y_max = max(paths[:, 0].max() + 1, 102)
    plt.ylim(y_min, y_max)
    plt.vlines(20, y_min, y_max, 'g', '--')
    plt.vlines(40, y_min, y_max, 'g', '--')
    plt.vlines(60, y_min, y_max, 'g', '--')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.savefig('phoenix_path_0.png')
    
    #计算所有路径的损益的平均值即为期权的价格
    print('3个月期限的凤凰期权的价格：',phoenix_value(paths, 3, 101, 85, 0.015))
    print('3个月期限的凤凰期权的delta：',phoenix_delta(paths, 3, 101, 85, 0.015))
    
    #考虑不同到期日和不同波动率下的期权价格
    sigmas = [0.2, 0.25, 0.3, 0.35, 0.4]
    ns = [3, 6, 9, 12]
    values, deltas = phoenix(100, sigmas, ns, 101, 85, 0.015)
    values, deltas = pd.DataFrame(values), pd.DataFrame(deltas)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    # 不同期限、波动率的期权的价格
    axes[0].plot(values, marker='o')
    axes[0].legend(values.columns, fontsize='large')
    axes[0].set_xticks(sigmas)
    axes[0].tick_params(labelsize=14)
    axes[0].set_ylabel('price', fontsize=14)
    axes[0].set_xlabel('volatility', fontsize=14)
    # 不同期限、波动率的期权的delta
    axes[1].plot(deltas, marker='^')
    axes[1].legend(deltas.columns, fontsize='large')
    axes[1].set_xticks(sigmas)
    axes[1].tick_params(labelsize=14)
    axes[1].set_ylabel('delta', fontsize=14)
    axes[1].set_xlabel('volatility', fontsize=14)
    axes[1].set_yticks([-0.35, -0.3, -0.25, -0.2, -0.15, -0.1])
    plt.savefig('phoenix_values_deltas.png')
