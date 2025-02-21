import pandas as pd
import numpy as np

from portfolio.portfolio import Portfolio
from mom_signal.mom_signal import MomentumSignal
from strategy.strategy import AbnormalMomentumStatey

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from alive_progress import alive_bar

class Backtest(Portfolio, MomentumSignal):  
    def __init__(self, portfolio: Portfolio):
            self.portfolio = portfolio 
            self.performance_dfs = []
            self.portfolio_features = []

    def run(self, abnormal=False, exclude_abnormal=False): 
        past_formation_dfs, future_holding_dfs = self.portfolio.get_walk_forward_splits()
        formed_portfolio_list = self.portfolio.get_formed_portfolio()
            
        # Run Backtest
        print("Backtest is running ...")
        with alive_bar(len(past_formation_dfs), force_tty=True) as bar: 
            for past_formation_period, future_holding_period, selected_stocks in zip(past_formation_dfs, future_holding_dfs, formed_portfolio_list):
                
                # Get formed portfolio
                mask_fields = ['r', 'benchmark', 'log_mcap']
                formed_portfolio = past_formation_period.stack(future_stack=True).loc[self.idx[:, selected_stocks], :]
                formed_portfolio = formed_portfolio[mask_fields]

                self.portfolio_features.append(formed_portfolio.copy())

                # Calculate Momentum Mesures
                formed_portfolio['CMOM'] = formed_portfolio.groupby(level=1)['r'].transform(lambda x: self.calculate_cmom(x))
                formed_portfolio['MMOM'] = formed_portfolio.groupby(level=1)['r'].transform(lambda x: self.calculate_mmom(x))
                formed_portfolio['TMOM'] = formed_portfolio.groupby(level=1)['r'].transform(lambda x: self.calculate_tmom(x))
                formed_portfolio['PMOM'] = self.calculate_pmom(formed_portfolio)
                
                formed_portfolio = formed_portfolio.dropna()
                
                
                # self.portfolio_features.append(formed_portfolio.copy())
                
                #################################################
                ##                                             ##
                ##        IMPLEMENT HDBSCAN HERE!!!!!!         ##
                ##                                             ##
                #################################################
                
                
                # Divide stocks in the portfolio into 3 market capitalization groups and for each group, 
                formed_portfolio['cap_groups'] = formed_portfolio['log_mcap'].transform(lambda x: pd.qcut(x, [0, .3, .7, 1], labels=['bottom', 'mid', 'top']))
                
                if abnormal:
                    # Find stocks with abnormal momentum 
                    formed_portfolio['mom_label'] = AbnormalMomentumStatey().find_cluster(formed_portfolio=formed_portfolio)

                    if exclude_abnormal: 
                        # Exclude stock fwith abnormal momentum to construct our portfolio
                        formed_portfolio.query('mom_label != -1', inplace=True)
                    else: 
                        # Filter out stock with abnormal momentum to construct our portfolio
                        formed_portfolio.query('mom_label == -1', inplace=True)
                
                # For each capitalization group, calculate weight of stocks in the portfolio
                formed_portfolio[['cmom_weights', 'mmom_weights', 'tmom_weights', 'pmom_weights']] = formed_portfolio.groupby('cap_groups', observed=True)[['CMOM', 'MMOM', 'TMOM', 'PMOM']].transform(lambda x: (1/len(x) * (x - x.mean())))
                
                # Get future return
                future_return = future_holding_period.loc[:, self.idx[:, selected_stocks]].stack(future_stack=True)[['r']]

                drop_cols = ['r', 'benchmark', 'CMOM', 'MMOM', 'TMOM', 'PMOM']
                
                # Create performance dataframe
                performance = (formed_portfolio.drop(columns=drop_cols)
                                        .droplevel(0)
                                        .reset_index()
                                        .merge(future_return.reset_index(), how='inner', left_on='ticker', right_on='ticker')
                                        .set_index(['time', 'ticker', 'cap_groups'])
                        
                              )
                
                self.performance_dfs.append(performance)
                
                bar() 