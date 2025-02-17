import pandas as pd

def calculate_portfolio_return(performnace_df, cummulative=True):
    weight_cols = ['cmom_weights', 'mmom_weights', 'tmom_weights', 'pmom_weights']
    names = {'cmom_weights': 'cmom_return', 'mmom_weights': 'mmom_return', 'tmom_weights': 'tmom_return', 'pmom_weights': 'pmom_return'}

    winner = performnace_df.copy() 
    winner[weight_cols] = winner[weight_cols].where(winner[weight_cols] > 0, 0)

    loser = performnace_df.copy() 
    loser[weight_cols] = loser[weight_cols].where(loser[weight_cols] < 0, 0)
    
    winner_ret = (
                winner[weight_cols]
                .mul(winner['r'].values.reshape(-1), axis='index')
                .mul(100)
                .rename(columns=names)
                ).groupby(level=2, observed=False).apply(lambda df: df.groupby(level=0, observed=False).sum().div(100))

    
    loser_ret = (
                -loser[weight_cols]
                .mul(loser['r'].values.reshape(-1), axis='index')
                .mul(100)
                .rename(columns=names)
                ).groupby(level=2, observed=False).apply(lambda df: df.groupby(level=0,observed=False).sum().div(100))

    
    arbitrage_ret = winner_ret - loser_ret
    
    if cummulative: 
        winner_ret = winner_ret.groupby(level=0, group_keys=False).apply(lambda df: df.add(1).cumprod().sub(1))
        loser_ret = loser_ret.groupby(level=0, group_keys=False).apply(lambda df: df.add(1).cumprod().sub(1))
        arbitrage_ret = arbitrage_ret.groupby(level=0, group_keys=False).apply(lambda df: df.add(1).cumprod().sub(1))
        
    
    return winner_ret , loser_ret, arbitrage_ret