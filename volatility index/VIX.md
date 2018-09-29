主要是基于2015年2月 - 2018年9月的50ETF期权的**日频**交易数据，按照新旧两种方式编制中国版的波动率指数（**VIX**）

1. 旧版VIX采用的是Whaley提出的方法，通过对多个接近平价的期权的隐含波动率加权得到，依赖于**Black-Scholes**公式
2. 新版VIX采用的是Demeterfi(1999)提出的方差互换和波动率互换的思想，不用依赖模型

## VIX_data_clean.py 

将从wind下载的数据作前期整理，主要是提取后面会用到的交易日期、执行价格，期权价格，期权的到期期限等信息；计算每个交易日对应的次月、次近月期限，要求次近月的剩余期限不少于7天；

## VIX_old.py

旧版VIX编制的Python程序，采用牛顿迭代法求解隐含波动率然后加权；

1. 选取最接近平值的执行价两个，稍高于平价和稍低于平价各一个，即实值程度最小和虚值程度最小的执行价格；
2. 然后取对应执行价格，近月和次近月的看涨期权（**call**)和看跌期权（**put**），共8个期权，计算每个交易对应8个期权的隐含波动率；
3. 对波动率依次按看涨期权与看跌期权的平均、执行价价格价差加权平均和剩余到期期限三次加权平均；
4. 最后即得到VIX指数；

![VIX_old](https://github.com/Jensenberg/volatility-and-option/blob/master/data/VIX_old.png)

## VIX_new.py

新版VIX编制的Python程序

$\sigma^2 = \frac{2} {T}  \sum\limits_i \frac{\Delta K_i}{K_i^2} Q(K_i) - \frac{1}{T} (\frac{F} {K_0} - 1)^2$

$VIX = 100 * \sqrt{\{T_1 \sigma^2[\frac {{NT}_2 - N_{30}}{{NT}_2 - {NT}_1}] + T_2 \sigma^2 [\frac { N_{30} - {NT}_1}{{NT}_2 - {NT}_1}]\} * \frac{N_{365}} {N_{30}} }$

参数详细解释见参考文献

![VIX_new](https://github.com/Jensenberg/volatility-and-option/blob/master/data/VIX_new.png)

## 参考文献

1. [VIX 指数及其衍生产品 - 中证指数](http://www.csindex.com.cn/uploads/researches/files/zh_CN/research_c_35.pdf) 
2. [VIX 指数浅析 - 永安期货](https://www.yafco.com/uploadfile/2013/1114/20131114103736428.pdf) 
3. [波动率指数简介 - 宏源期货](http://www.hongyuanqh.com/download/20150331/%E6%B3%A2%E5%8A%A8%E7%8E%87%E6%8C%87%E6%95%B0%E7%AE%80%E4%BB%8B.pdf) 
4. [VIX Index Rules and Methodology-Cboe](http://www.cboe.com/micro/vix/vix-index-rules-and-methodology.pdf)
