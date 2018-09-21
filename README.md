# volatility
计算波动率的六种方法：

Volatility | Price Information

-------------|------------------------

Realized|Close 

Parkinson|High，Low

Garman-Klass| Open, High, Low, Close

Roger-Satchell | Open, High, Low, Close

Garman-Klass-Yang-zhang | Open, High, Low, Close

Yang-Zhang | Open, High, Low, Close

##1. Realized Volatility: Close-Close

$\sigma_{realized} = \sqrt{  \frac{N}{n-2} \sum\limits_{i=1} ^{n-1} (r_t - \bar r)^2  }$   

 $r_t =\log\frac{C_t}{C_{t-1}}$：收益率

$ \bar r =\frac{1}{n} \sum\limits_{n}^{t=1}r_t$：平均收益率

## 2.Parkinson Volatility: High-Low Volatility

$\sigma_{parkinson} = \sqrt{ { \frac{1}{4*\ln{2}} * \frac{252}{n} * \sum\limits_{t=1}^{n} {\ln{(\frac{H_t}{L_t})}}^2}}$

一般的波动率只考虑了收盘价，Parkinson Volatility 将最高价和最低价纳入了考虑范围，underestimate

## 3. Garman-Klass Volatility: OHLC volatility

Assumes Brown motion with zero drift and no opening jumps.

$\sigma_{garman-klass} = \sqrt{\frac{N}{n} \sum\limits_{i=1}^{N} \lbrack {\frac{1}{2} * (\log{\frac{H_i}{L_i}})^2 -(2*\log2 -1) * (\log\frac{C_i}{O_i})^2\rbrack}}$

相比于Parkinson Volatility进一步考虑了开盘价和收盘价，纳入了更多的价格信息， underestimate

## 4. Roger-Satchell Volatility: OHLC Volatility

Assumes for non-zero drift, but assumed no opening jump. 

$\sigma_{roger-satchel} = \sqrt{ \frac{N}{n} \sum\limits_{i=1}^{n} \lbrack \log \frac{H_i}{L_i} * \log \frac{H_i}{O_i} + \log \frac{HL_i}{L_i} * \log \frac{L_i}{O_i} \rbrack }$

underestimate

## 5. Garman-Klass-Yang-Zhang Volatility: OHLC Volatility

A modified version of Garman-Klass estimator that allows for opening jumps.





