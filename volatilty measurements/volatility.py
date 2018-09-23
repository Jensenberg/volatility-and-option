# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 21:10:24 2018

@author: 54326
"""

from math import sqrt, log

def realized(close, N=240):
    '''
    计算实现的波动率，等于日收益率的标准差，仅利用了收盘价的信息
    close:
        收盘价，要计算n天的波动率，需要n+1天的收盘价
    N:
        一年的交易天数，国内一年交易天数约为240多天，为了方便计算，取为240天
    '''
    rt = list(log(C_t / C_t_1) for C_t, C_t_1 in zip(close[1:], close[:-1]))
    rt_mean = sum(rt) / len(rt)
    return sqrt(sum((r_i - rt_mean) ** 2 for r_i in rt) * N / (len(rt) - 1))
    
def parkinson(high, low, N=240):
    '''
    计算Parkinson波动率，仅利用了日内的最高价和最低价
    '''
    sum_hl = sum(log(H_t / L_t) ** 2 for H_t, L_t in zip(high, low))
    return sqrt(sum_hl * N / (4 * len(high) *log(2)))

def garman_klass(open, high, low, close, N=240):
    '''
    计算Garman-Klass波动率，利用了开、高、低、收四种价格信息，假定四种价格序列是等长的，下同
    '''
    sum_hl = sum(log(H_t / L_t) ** 2 for H_t, L_t in zip(high, low)) / 2
    sum_co = sum(log(C_t / O_t) ** 2 
                 for C_t, O_t in zip(close, open)) * (2 * log(2) - 1)
    return sqrt((sum_hl - sum_co) * N / len(close))

def roger_satchell(open, high, low, close, N=240):
    '''
    计算Roger-Satchell波动率
    '''
    sum_ohlc = sum(log(H_t / C_t) * log(H_t / O_t)
                 + log(L_t / C_t) * log(L_t / O_t)
                   for O_t, H_t, L_t, C_t in zip(open, high, low, close))
    return sqrt(sum_ohlc * N / len(close))

def garkla_yangzh(open, high, low, close, N=240):
    '''
    计算Garman-Klass-Yang-Zhang波动率
    '''
    sum_oc_1 = sum(log(O_t / C_t_1) ** 2
                   for O_t, C_t_1 in zip(open[1:], close[:-1]))
    sum_hl = sum(log(H_t / L_t) ** 2
                 for H_t, L_t in zip(high[1:], low[1:])) / 2
    sum_co = sum(log(C_t / O_t) ** 2
                 for C_t, O_t in zip(close[1:], open[1:])) *(2 * log(2) - 1)
    return sqrt((sum_oc_1 + sum_hl - sum_co) * N / (len(close) - 1))

def yang_zhang(open, high, low, close, N=240):
    '''
    计算Yang-Zhang波动率
    '''
    oc = list(log(O_t / C_t_1) for O_t, C_t_1 in zip(open[1:], close[:-1]))
    n = len(oc)
    oc_mean = sum(oc) / n
    oc_var = sum((oc_i - oc_mean) ** 2 for oc_i in oc) * N / (n - 1)
    
    co = list(log(C_t / O_t) for O_t, C_t in zip(open[1:], close[1:]))
    co_mean = sum(co) / n
    co_var = sum((co_i - co_mean) ** 2 for co_i in co) * N / (n - 1)
    
    rs_var = (roger_satchell(open[1:], high[1:], low[1:], close[1:])) ** 2
    
    k = 0.34 / (1.34 + (n +1) / (n - 1))
    
    return sqrt(oc_var + k * co_var + (1-k) * rs_var)

def volatility(model, open=None, high=None, low=None, close=None, N=240):
    '''
    Parameters:
        model:
            计算波动率的模型，上述六种中的一种
    Returns:
        date:
            计算波动率的当前日期
        并返回相应的年化波动波动率
    '''    
    if close is not None:
        date = close.index[-1]
    elif high is not None:
        date = high.index[-1]
    if model == 'realized':
        return date, realized(close, N)
    elif model == 'parkinson':
        return date, parkinson(high, low, N)
    elif model in ('garman_klass', 'roger_satchell',
                   'garkla_yangzh','yang_zhang'):
        return date, eval(model)(open, high, low, close, N)
    else:
        print('model must be one kind of these models: realized, ', end=' ')
        print('parkinson, garman_klass, garkla_yangzh, yang_zhang')
        return None
                
def rolling_volatility(model, window, open=None, high=None, low=None, 
                       close=None, N=240, **kwargs):
    '''
    计算滚动窗口的波动率，为了可比性，每种方法的收益率观测值数量等于窗口长度，从而同样窗口下
    每种方法需要的交易日数略有区别
    Parameters:
        model:
            使用的模型
        window：
            设定的窗口期长度
    Returns:
        vol:
            dict, 返回一个以日期为键，波动率为值的字典
    '''
    vol = {}        
    if model == 'realized':
        num = len(close)
        for i in range(num - window):
            close_i = close[i: window + i + 1]
            index_i = close_i.index[-1]
            vol[index_i] = realized(close_i, N)
    elif model == 'parkinson':
        num = len(high)
        for i in range(num - window + 1):
            high_i = high[i: window + i]
            low_i = low[i: window + i]
            index_i = high_i.index[-1]
            vol[index_i] = parkinson(high_i, low_i, N)
    elif model in ('garman_klass', 'roger_satchell'):
        num = len(close)
        for i in range(num - window + 1):
            s = slice(i, window + i)
            open_i = open[s]; high_i = high[s]
            low_i = low[s]; close_i = close[s]
            index_i = close_i.index[-1]
            vol[index_i] = eval(model)(open_i, high_i, low_i, close_i, N)
    elif model in ('garkla_yangzh', 'yang_zhang'):
        num = len(close)
        for i in range(num - window):
            s = slice(i, window + i + 1)
            open_i = open[s]; high_i = high[s]
            low_i = low[s]; close_i = close[s]
            index_i = close_i.index[-1]
            vol[index_i] = eval(model)(open_i, high_i, low_i, close_i, N)
    else:
        print('model must be one kind of these models: realized, ', end=' ')
        print('parkinson, garman_klass, garkla_yangzh, yang_zhang')
        return None
    
    return vol
            
if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt
    
    zz500 = pd.read_excel('e:/alpha/zz500.xlsx') 
    zz500.set_index(pd.to_datetime(zz500['date']), inplace=True)
    test = zz500[:60]
    
    models = ['realized', 'parkinson', 'garman_klass', 'roger_satchell',
              'garkla_yangzh', 'yang_zhang']
    
    kwargs = {'open': test['open'], 'high': test['high'],
              'low': test['low'], 'close': test['close']}
#    限定了交易日数，收益率的观测数量存在一定不同
    for model in models:
        print(volatility(model, **kwargs))
    
    kw = {'open': zz500['open'], 'high': zz500['high'], 
          'low': zz500 ['low'], 'close': zz500['close']}
    window = 60
    vols = {}
    for model in models:
        vols[model] = pd.Series(rolling_volatility(model, window, **kw))
    vols = pd.DataFrame(vols)

    fig, axes = plt.subplots(1, 2 , figsize=(16, 8), 
                             sharex=True, sharey=True)
    xz = range(len(vols))
#    xn = vols.index.strftime('%Y-%m')
    for column in ['parkinson', 'garman_klass', 'roger_satchell']:
        axes[0].plot(xz, vols[column], label=column)# 仅利用了当日的价格信息
    axes[0].legend(fontsize='large')
    for column in ['realized', 'garkla_yangzh', 'yang_zhang']:
        axes[1].plot(xz, vols[column], label=column) # 利用了前一日和当日的价格信息
    axes[1].legend(fontsize='large')
    plt.subplots_adjust(wspace=0.02)
    plt.xlim(0, len(vols)+1)
    days = vols.index.year.value_counts().sort_index().cumsum()
    plt.xticks(days, days.index[1:])#在每年年初标记刻度
#    plt.xticks(xz[::240], xn[::240]) # 从开始日期起每隔一年标记一次刻度
    fig.suptitle('Volatility Measurements', fontsize=16, y=0.92)
    plt.savefig('vlolatilities.png', bbox_inches='tight')
    