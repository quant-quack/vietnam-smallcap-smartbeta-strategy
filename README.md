# Vietnam Smart Beta Strategy: Optimizing Returns & Risk with Principal Component Momentum

## Introduction
The momentum effect, where stocks with high past performance continue to outperform those with poor past performance, has been well-documented in developed markets like the U.S. However, studies on Asian stock markets often reveal a negative momentum effect, where past losers tend to outperform past winners [Eom and Park](https://doi.org/10.1016/j.ribaf.2023.101908). This anomaly presents an opportunity to construct a Smart Beta Strategy that capitalizes on this negative momentum. This project verifies the negative momentum effect in the Vietnamese stock market using the Principal Component Momentum approach proposed by Eom and Park. Leveraging this effect, it further introduces a methodology for constructing and optimizing a Smart Beta Portfolio tailored to the Vietnamese market.

## Data and Methodology

### Data
The data for this project is collected from multiple sources using various methods. It includes historical and fundamental data for 1,698 stocks (both listed and delisted) from 2002 to 2023. However, due to data source limitations, fundamental data is only available from 2013, so the backtest period is limited to 2013–2023.

**Stock selection process**

1. **Exclusions**  
    - Financial sector stocks.  
    - Stocks missing market capitalization or book-to-market equity ratio data.
    
2. **Selection Criteria (for each subperiod)**  
    - Complete return data for momentum calculations.  
    - Complete price and share outstanding data for market cap and investment weight calculations.  
    - Trading volume data available, with valid non-zero returns on at least 50% of trading days.
    
3. **Filtering for Extreme Values & Micro-Small Firms**  
    - Stocks in the **top 5% by volatility** (past standard deviation of daily returns) are excluded.  
    - Stocks in the **bottom 5% by market capitalization** (measured in June) are excluded.

### Methodology

#### Principal Component Momentum

Principal Component Momentum (PMOM) is calculated based on Cross-Sectional Momentum (CMOM), Time Series Momentum (TMOM), and Moving Average Momentum (MMOM). The momentum measures are computed using the following equations.

1. **Cross-Sectional Momentum (CMOM)**
```math
MOM^{(k=1)}_j = \prod_{i=2}^{J} (1+R_{j,t-i}) - 1
```
where:
- `k = 1` represents CMOM
- `R_j` represents the monthly returns of stock `j`
- `i = 2, 3, ..., J` because the previous month `(t - 1)` of the testing month is excluded
- `J` indicates the starting month of the past formation period, that is, `J=12` months `(t - 12)`

1. **Moving-Average Momentum (MMOM)**
```math
MOM^{(k=2)}_j = SP_j - LP_j
```
where:
- `k = 2` represents MMOM
- $SP_j$ and $LP_j$ represent the short- and long-term performance of stock `j`, respectively
```math
SP = \prod_{i=2}^{S} (1+R_{t-i}) - 1
```
```math
LP = \prod_{i=2}^{L} (1+R_{t-i}) - 1
```
where:
- The length of the short-term period `S` is one month `(t–2)`, and that of the long-term period `L` is equal to the past formation period, that is, $L \equiv J$

1. **Time-Series Momentum (TMOM)**
```math
MOM^{(k=3)}_j = |\overline{TS_j}| \times \overline{S_j}
```
where:
- `k = 3` represents TMOM
- $\overline{S_j}$ is the average signal of the long and short positions
- $|\overline{TS_j}|$ is the absolute value of the average period performance
```math
\overline{S_j} = \frac{1}{J-1} \sum_{i=2}^{J} S_{j,t-i}
```
```math
S_{t-m} = \text{sign} \left( \frac{1}{M} \sum_{n=0}^{M-1} (M-n) R_{t-m-n} \right)
```
```math
\overline{TS_j} = \frac{1}{J-1} \sum_{i=2}^{J} TS_{j,t-i}
```
```math
TS_{t-m} = \frac{1}{M} \sum_{n=0}^{M-1} (M-n) R_{t-m-n}
```

1. **Principal Component Momentum (PMOM)**
```math
MOM^{(k=4)}_j = \sum_{k=1}^{3} \left[ VE^{(1)}_{j,k} \times MOM^{(k)}_j \right]
```
where:
- `k = 4` represents the PMOM
- The cross-sectional data of CMOM `(k = 1)`, MMOM `(k = 2)`, and TMOM `(k = 3)` for `N` stocks are used as input data for PCA
- $VE^{(1)}_{j,k}$ is the eigenvector

#### Arbitrage-weighting Method

The **arbitrage-weighting method** is used to classify stocks into two groups: winners and losers.

1. Stocks with a momentum measure $MOM_j^{(k)}$ higher than the average value $MOM^{(k)}$ are assigned **positive weights** $(w_j > 0)$ and classified into the **winner portfolio** $(W)$.
2. Stocks with a momentum measure lower than the average value are assigned the **absolute values of negative weights** $(w_j \leq 0, |w_j|)$ and included in the **loser portfolio** $(L)$.

```math
w_j^{(W)} =
\begin{cases} 
    w_j, & w_j > 0 \\ 
    |w_j|, & w_j \leq 0 
\end{cases}
```
where
```math
w_j = \frac{MOM_j^{(k)} - MOM^{(k)}}{N}, \quad k = 1,2,3,4.
```
### Backtesting Periods
109 months, from July 2013 to June 2023

- **Formation and Holding Periods**
  - Past formation period: **12 months.**
  - Future holding period: **one month.**
- **Rolling of Subperiods**
  - The rolling of the subperiods adopts the non-overlapping holding period method.

## Empirical Verification
![Price behaviour of different market capitalization groups](/reports/visualization/empirical_verification.png)
## Portfolio Optimization with Tracking-Error Constraints for Vietnam Stock Market
![Impact of Scaling Factor on Sharpe Ratio](/reports/visualization/impact_of_lambda.png)
## Performance Report
![Performance Dashboard (Out-of-sample)](/reports/visualization/performance_dashboard.png)

