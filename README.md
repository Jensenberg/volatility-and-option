## data

包含各个程序运行需要的数据，以及用于展示结果的一些图表

1. Excel文件为最原始的从wind导出的数据
2. h5文件则主要经过整理后的可以直接使用的数据，读取速度更快

##  volatility measurements

计算波动率的六种方法：

(1) Realized 

(2) Parkinson 

(3) Garman-Klass 

(4) Roger-Satchell

(5) Garman-Klass -Yang-Zhang

(6) Yang-Zhang

以2005.01-2018.09的中证500指数的OHLC数据，进行了测试

## implied volatility

构造一个期权，利用实盘价格作为路径，以Monte-Carlo模拟和期权动态对冲为基础，计算中证500指数的隐含波动率；

## volatility index

按照两种方式编制基于50ETF期权的VIX指数，采用的是日频数据，指数的最高点出现在2015年8月25左右，当前（2018年9月21日）为20点左右；

## phoenix autocall

通过蒙特卡洛模拟对凤凰期权进行定价，计算delta值