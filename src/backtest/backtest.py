class Backtest: 
    def __init__(self, long_df_daily, long_df_monthly): 
        self.long_df_daily = long_df_daily
        self.long_df_monthly = long_df_monthly
        
    
    def __transform_into_rolling_df(self): 
        unstack_tmp = self.long_df_monthly.unstack()
        periods = self.long_df_monthly.index.get_level_values(0).unique()

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
    
    def get_rolling_df(self): 
        return self.__transform_into_rolling_df()