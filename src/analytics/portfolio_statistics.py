import pandas as pd
from empyrical import annual_return, annual_volatility, max_drawdown, sharpe_ratio, sortino_ratio, calmar_ratio

def create_portfolio_statistics(performance): 
    metrics = ["Annual return",
                "Annual volatility",
                "Max drawdown",
                "Sharpe ratio",
                "Sortino ratio",
                "Calmar ratio"]
    
    results = pd.DataFrame(index=metrics)
    
    for group, df in performance.groupby(level=0): 
        stats = [
            annual_return(df.pmom_return, period='monthly'),
            annual_volatility(df.pmom_return, period='monthly'),
            max_drawdown(df.pmom_return),
            sharpe_ratio(df.pmom_return, period='monthly'),
            sortino_ratio(df.pmom_return, period='monthly'),
            calmar_ratio(df.pmom_return, period='monthly')
        ]    
        results[group] = stats
    
    return results