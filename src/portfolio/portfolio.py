import pandas as pd
import numpy as np

class Portfolio:
    idx = pd.IndexSlice 

    def __init__(self, long_daily, long_monthly): 
        self.long_daily = long_daily
        self.long_monthly = long_monthly
        
        
    def __walk_forward_splits(self): 
        tmp = self.long_monthly.copy()  
        unstack_tmp = tmp.unstack()
        periods = tmp.index.get_level_values(0).unique()

        past_formation = []
        future_holding = []

        for i in range(len(periods)-11): 
            past_formation.append(periods[i:i+11].normalize())
            future_holding.append(periods[i+11].normalize())
            
        # Create past formation dataframes
        past_formation_dfs = []
        future_holding_dfs = []

        for sub_period in past_formation: 
            past_formation_dfs.append(unstack_tmp.loc[sub_period])

        for sub_period in future_holding: 
            future_holding_dfs.append(unstack_tmp.loc[[sub_period]])
        
        return past_formation_dfs, future_holding_dfs
         
    def __filter_condition_1(self, df): 
        tmp = df.copy()
        selected_stocks = set(tmp['book_to_market'].dropna(axis=1).columns)
        
        return selected_stocks

    def __filter_condition_2(self, df): 
        tmp = df.copy()
        
        # 1. All return data to calculate the momentum measures in the subperiod are available 
        selected_stocks = set(tmp['r'].dropna(axis=1).columns)

        # 2. All price data and the number of shares ourstanding in the past period are available to calculate investment weight and market capitalization 
        selected_stocks = selected_stocks.intersection(tmp['log_mcap'].dropna(axis=1).columns)

        # 3. Among stocks with all trading volume data during the past formation period, stocks with valid non-zero return data on 50% or more trading days are available 
        check = self.long_daily.loc[self.idx[tmp.index.min()-pd.offsets.MonthEnd()+pd.DateOffset(1):tmp.index.max(), :], :].unstack()
        na_less_than_5_pct = (check['volume'].isnull().sum() / len(check) < .05)
        satis_cond = na_less_than_5_pct[na_less_than_5_pct == True].index
        selected_stocks = selected_stocks.intersection(check['volume'][satis_cond].dropna(axis=0).columns)

        valid_df = (check['r'][list(selected_stocks)].eq(0).sum() / len(check['r'][list(selected_stocks)]) < .5).to_frame(name='valid_r')
        selected_stocks = set(valid_df[valid_df['valid_r'] == True].index)
        
        return selected_stocks

    def __filter_condition_3(self, df, stocks):
        tmp = df.copy()
        stocks = list(stocks)

        check = tmp.loc[:, self.idx[:, stocks]]
        daily_subset = self.long_daily.loc[self.idx[tmp.index.min()-pd.offsets.MonthEnd()+pd.DateOffset(1):tmp.index.max(), :], :].unstack()['r'][stocks]
        
        volatility = daily_subset.replace(np.inf, np.nan).std()
        mcap = check['log_mcap'].iloc[-1]

        # 1. Exclude stocks with extreme volatility
        volatility_95th_percentile = volatility.quantile(.95)
        valid_volatility = (volatility <= volatility_95th_percentile).to_frame(name='valid_vol')
        filtered_volatility = set(valid_volatility[valid_volatility['valid_vol'] == True].index)

        # 2. Exclude micro-small firms
        mcap_5th_percentile = mcap.quantile(.05)
        valid_mcap = (mcap >= mcap_5th_percentile).to_frame(name='valid_cap')
        filtered_mcap = set(valid_mcap[valid_mcap['valid_cap'] == True].index)
        
        selected_stocks = filtered_volatility.intersection(filtered_mcap)
        
        return selected_stocks


    def __form_portfolio(self):
        past_formation_dfs, _ = self.get_walk_forward_splits()
        
        portf_list = []
        
        for period in past_formation_dfs: 
            # Filter condition 1
            passed_cond_1 = self.__filter_condition_1(period)

            # Filter condition 2
            passed_cond_2 = passed_cond_1.intersection(self.__filter_condition_2(period))

            # Filter condition 3
            passed_cond_3 = self.__filter_condition_3(period, passed_cond_2) # => Runtime warning come from condition 3
            
            portf_list.append(list(passed_cond_3))

        return portf_list
        
    def get_formed_portfolio(self): 
        return self.__form_portfolio()  
    
    def get_walk_forward_splits(self): 
        return self.__walk_forward_splits()
    