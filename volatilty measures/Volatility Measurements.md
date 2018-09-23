# volatility
计算波动率的六种方法（仅供参考）：

| Volatility              | Price Information      |
| ----------------------- | ---------------------- |
| Realized                | Close                  |
| Parkinson               | High，Low              |
| Garman-Klass            | Open, High, Low, Close |
| Roger-Satchell          | Open, High, Low, Close |
| Garman-Klass-Yang-Zhang | Open, High, Low, Close |
| Yang-Zhang              | Open, High, Low, Close |

后五种方法均采用了连续收益率，导致波动率被低估

## 中证500指数的波动率的计算结果如下图所示

![中证500指数的波动率](https://github.com/Jensenberg/volatility-and-Option/blob/master/data/vlolatilities.png)

Parkinson，Garman-Klass，Roger-Satchell都是只用到当日的价格信息，可以看做是日内波动率；

Realized，Garman-Klass-Yang-Zhang，Yang-Zhang都用到了前一日和当日的价格信息，可以看做是日间波动率，从图上来看，前三者得到的波动率明显小于后三者得到波动率。 

## 1. Realized Volatility: Close-Close

$$\sigma_{realized} = \sqrt{  \frac{N}{n-2} \sum\limits_{i=1} ^{n-1} (r_t - \bar r)^2  }$$   

$r_t =\log\frac{C_t}{C_{t-1}}$：收益率

$ \bar r =\frac{1}{n} \sum\limits_{n}^{t=1}r_t$：平均收益率

## 2. Parkinson Volatility: High-Low Volatility

$$\sigma_{parkinson} = \sqrt{ { \frac{1}{4*\ln{2}} * \frac{252}{n} * \sum\limits_{t=1}^{n} {\ln{(\frac{H_t}{L_t})}}^2}}$$

一般的波动率只考虑了收盘价，Parkinson Volatility 将最高价和最低价纳入了考虑范围，underestimate

## 3. Garman-Klass Volatility: OHLC volatility

Assumes Brown motion with zero drift and no opening jumps.

$$\sigma_{garman-klass} = \sqrt{\frac{N}{n} \sum\limits_{i=1}^{N} \lbrack {\frac{1}{2} * (\log{\frac{H_i}{L_i}})^2 -(2*\log2 -1) * (\log\frac{C_i}{O_i})^2\rbrack}}$$

相比于Parkinson Volatility进一步考虑了开盘价和收盘价，纳入了更多的价格信息， underestimate

## 4. Roger-Satchell Volatility: OHLC Volatility

Assumes for non-zero drift, but assumed no opening jump. 

$$\sigma_{roger-satchel} = \sqrt{ \frac{N}{n} \sum\limits_{i=1}^{n} \lbrack \log \frac{H_i}{L_i} * \log \frac{H_i}{O_i} + \log \frac{HL_i}{L_i} * \log \frac{L_i}{O_i} \rbrack }$$

underestimate

## 5. Garman-Klass-Yang-Zhang Volatility: OHLC Volatility

A modified version of Garman-Klass estimator that allows for opening jumps.

$$\sigma_{garkla-yangzh} = \sqrt { \frac{N}{n} \sum\limits_{i=1}^{n} \lbrack (\log \frac{O_i}{C_{i-1}})^2 +  {\frac{1}{2} * (\log{\frac{H_i}{L_i}})^2 -(2*\log2 -1) * (\log\frac{C_i}{O_i})^2}\rbrack }$$

当资产收益率均不为零时，会高估波动率

## 6. Yang-Zhang Volatility: OHLC Volatility 

$$\sigma_{yang-zhang} = \sqrt {\sigma_o^2 + k * \sigma_c^2 + (1-k) * \sigma_{rs}^2}$$

$\mu_o = \frac{1}{n} \sum\limits_{i=1}^{n} \log \frac {O_i}{C_{i-1}}$

$\sigma_o^2  = \frac{N}{n-1} \sum\limits_{i=1}^{n} (\log \frac {O_i}{C_{i-1}} - \mu_o)^2$, 		Open-Close Volatility or Overnight Volatility

$\mu_c = \frac{1}{n} \sum\limits_{i=1}^{n} \log \frac {C_i}{O_i}$ , 	Close-Open Volatility

$\sigma_c^2  = \frac{N}{n-1} \sum\limits_{i=1}^{n} (\log \frac {C_i}{O_i} - \mu_c)^2$

$\sigma_{rs}^2 = \sigma_{roger-satchel}^2$

$k^* = \frac {\alpha} {1+ \alpha + \frac{n+1}{n-1}},    \alpha$通常为0.34

Has minimum estimator error, and is independent of drift and open gaps. It van be interpreted as a weighted average of the Roger-Satchell estimator, the Close-Open Volatility and the Open-Close Volatility.


### Reference：

1. [ Volatility and its Measurements](https://www.eurexchange.com/blob/116048/47ca53f0178cec31caeecdf94cc18f6e/data/volatility_and_its_measurements.pdf.pdf)

2. [ Drift Independent Volatility Estimation Based on High, Low, Open and Close Price](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.628.4037&rep=rep1&type=pdf)

3. [volatility function | R Documentation](https://www.rdocumentation.org/packages/TTR/versions/0.23-3/topics/volatility)

4. [Parkinson volatility - Breaking Down Finance](http://breakingdownfinance.com/finance-topics/risk-management/parkinson-volatility/)

5. [MEASURING HISTORICAL VOLATILITY](http://www.todaysgroep.nl/media/236846/measuring_historic_volatility.pdf)

   
