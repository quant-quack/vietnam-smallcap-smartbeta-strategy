# Vietnam Smart Beta Strategy: Optimizing Returns & Risk with Principal Component Momentum

## Introduction

The **momentum effect**, where **stocks with strong past performance continue to outperform** those with weak past performance, has been well-documented in **developed markets** like the **U.S.** However, studies on **Asian stock markets** often reveal a **negative momentum effect**, where **past losers tend to outperform past winners** [Eom and Park](https://doi.org/10.1016/j.ribaf.2023.101908). This anomaly presents an opportunity to construct a **Smart Beta Strategy** that **capitalizes on negative momentum**.  

This project is inspired by the research of **Eom & Park** and aims to **verify the negative momentum effect** in the **Vietnamese stock market** using the **Principal Component Momentum approach** they proposed. Leveraging this effect, it further introduces a methodology for **constructing and optimizing a Smart Beta Portfolio** tailored to the **Vietnamese market**.

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
### Backtesting Framework and Periodicity
109 months, from July 2013 to June 2023

- **Formation and Holding Periods**
  - Past formation period: **12-month.**
  - Future holding period: **1-month.**
- **Rolling of Subperiods**
  - The rolling of the subperiods adopts the non-overlapping holding period method.

## Empirical Verification
To examine the **negative momentum effect** in the **Vietnamese market**, the **size-momentum portfolio** is constructed following the methodology of the original paper:  
- **Step 1: Market Capitalization Classification**  
  - All stocks are sorted by market capitalization and divided into three groups: **top 30%**, **middle 40%**, and **bottom 30%**.  
- **Step 2: Size-Based Grouping**  
  - The **top 30%** is classified as the **large-cap group**, while the **bottom 30%** is classified as the **small-cap group**.  
- **Step 3: Momentum-Based Sorting**  
  - Within both the **large-cap** and **small-cap** groups, stocks are further classified into **winner** and **loser** portfolios using the **arbitrage-weighting method**.
![Price behaviour of different market capitalization groups](/reports/visualization/empirical_verification.png)  
*Figure 1: The image illustrates the price behavior of different market capitalization groups within the winner, loser, and arbitrage portfolios.*

The visualization of **stock price behavior** across different **capitalization groups** in the **momentum portfolio** confirms the presence of the **negative momentum phenomenon** in the **Asian market overall and specifically in Vietnam**. This is evident in the **future holding period (or `out-of-sample period`)** performance of the **`Arbitrage Portfolio`** within the **small-cap group**, as reflected in the **declining cumulative return trend through the performance of `PMOM`**. This suggests that **stocks with strong past performance (Winner Stocks) tend to underperform** compared to those with **weaker past performance (Loser Stocks)**. A **similar pattern** is observed in the **mid-cap group**, whereas in the **large-cap group, the positive momentum effect is confirmed**.

The **abnormal performance of loser stocks** across all three **capitalization groups** presents an opportunity to construct a **smart beta portfolio**. For a more **intuitive perspective**, let's examine the **performance of the three capitalization groups** within the **loser portfolio** through the table below.

| Metric           | Bottom  | Mid     | Top     |
|:-----------------:|:---------:|:---------:|:---------:|
| Annual return   | 0.0696  | 0.0440  | 0.0149  |
| Annual volatility | 0.0750  | 0.0843  | 0.0697  |
| Max drawdown   | -0.1642 | -0.2113 | -0.1696 |
| Sharpe ratio   | 0.9370  | 0.5539  | 0.2464  |
| Sortino ratio  | 1.5540  | 0.9244  | 0.3596  |
| Calmar ratio   | 0.4239  | 0.2084  | 0.0877  |


## Small-cap Smart Beta Strategy for Vietnam Stock Market
The **loser stocks in the small-cap group** exhibit **significantly superior performance** compared to those in the **mid-cap and large-cap groups**. Consequently, this segment is selected as the **universe** for constructing the **smart beta momentum portfolio** tailored for the **Vietnamese market**.  

However, only the **top 30% of stocks with the most negative momentum** within the **loser portfolio of the small-cap group** are included in the portfolio construction.  

Since **short selling is not permitted** in Vietnam, adjustments are necessary to align with **market constraints** while preserving the **momentum allocation structure** of the **arbitrage-weighting method**—where **stocks with momentum deviations further from the mean receive larger weights**.

![Arbitrage Weighting Method]( /reports/visualization/arbitrage_weighting.png )  
*Figure 2: The image illustrates the momentum of individual stocks and the average momentum. Stocks with higher fluctuations relative to the mean (e.g., stock C) receive a higher weight allocation, whereas stocks with lower fluctuations (e.g., stock B) receive a lower weight allocation.*

To accommodate a **long-only portfolio** while ensuring **all weights remain positive** and sum to **one**, we apply the softmax function as a transformation mechanism. For each portfolio weight vector $\mathbf{w}$ in the future holding period:
```math
w'_i = \frac{e^{w_i}}{\sum_{j} e^{w_j}}, \quad w'_i > 0, \quad \sum_{i} w'_i = 1.
```
**Small-cap stocks** also tend to exhibit superior performance in **January**, consistent with the findings of [Haug and Hirschey (2006)](https://doi.org/10.2469/faj.v62.n5.4284), under the adjusted backtesting framework:  

#### Backtesting Framework and Periodicity

121 months, spanning `January 2013` to `December 2023`.  

#### Formation and Holding Periods  
- **Formation period**: 12-month.  
- **Holding period**: 1-month.  

#### Rolling of Subperiods  
Subperiods are rolled using a **non-overlapping holding period** approach.  

The adjusted **out-of-sample** portfolio performance is summarized as follows.

![Small-Cap Smart Beta Performance](/reports/visualization/sml_smart_beta_performance.png)

### Performance Metrics  

| Metric            | Small-Cap Smart Beta  |
|:------------------:|:------:|
| **Annual return**      | 0.3521  |
| **Annual volatility**  | 0.3040  |
| **Max drawdown**       | -0.5632 |
| **Sharpe ratio**       | 1.0646  |
| **Sortino ratio**      | 2.2736  |
| **Calmar ratio**       | 0.6251  |


## Portfolio Optimization

The proposed strategy delivers an annual return of approximately **35%** (excluding additional costs), exhibiting relative stability. However, with a portfolio standard deviation of around **30%**, the **Sharpe ratio is not particularly appealing**, whereas the **Sortino ratio appears more favorable**.  

To enhance risk-adjusted performance, we may seek to **minimize portfolio variance**, while ensuring that **portfolio weights do not deviate significantly** from the folded portfolio structure—preserving the allocation framework dictated by the **momentum-based arbitrage-weighting method**.  

This leads to the following portfolio optimization problem...

### Regularized Global Minimum Variance (GMV) Portfolio  
#### Optimization Problem:  
```math
\min_w w^\top \Sigma w + \lambda \|w - w^{\text{index}}\|_{2}
```

$$
st:  
\mathbf{1}^\top w = 1, \quad w \geq 0
$$

where:
- $w$: Portfolio weight vector  
- $\Sigma$: Covariance matrix of asset returns  
- $w^{\text{index}}$: Momentum Index Weight Vector generated from the portfolio constructed above.
- $\lambda$: Regularization parameter controlling deviation from the benchmark  
- $\mathbf{1}^\top w = 1$: Budget constraint
- $w \geq 0$: Long-only constraint

To determine the suitable hyperparameter **λ**, we examine how the **Sharpe ratio** changes with different **λ** values, as depicted in the following figure. **Important note:** The illustration reflects the relationship between **λ** and the **Sharpe ratio** based on **in-sample data**.
![Impact of Scaling Factor on Sharpe Ratio](/reports/visualization/impact_of_lambda.png)
*Figure 4: Impact of λ on the Sharpe ratio. The chart illustrates the relationship between λ and the Sharpe ratio based on in-sample data.*

Based on the visualization, the **Sharpe ratio peaks** in the range of **0–0.01** and **converges to zero** as **λ** increases. Therefore, we select **λ** that maximizes the **Sharpe ratio** and proceed with **backtesting the portfolio using out-of-sample data** after solving the **optimization problem**.

## Performance Report
![Performance Dashboard (Out-of-sample)](/reports/visualization/performance_dashboard.png)

