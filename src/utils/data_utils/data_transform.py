import pandas as pd
import numpy as np  

class DataTransform:
    idx = pd.IndexSlice

    def __init__(self, benchmark, fun_data, hist_data, start_time='2013-01-01'): 
        self.benchmark = benchmark
        self.fun_data = fun_data
        self.hist_data = hist_data        
        self.start_time = start_time
        
    def __transform_data(self): 
        daily = self.hist_data.copy()
        
        long_daily = daily.set_index(['time', 'ticker'])
        long_daily['r'] = long_daily.groupby(level=1)['close'].ffill().transform(lambda x: x.pct_change())

        monthly_close = long_daily.unstack()['close'].resample('ME').last().stack(future_stack=True).to_frame(name='close')
        monthly_vol = long_daily.unstack()['volume'].resample('ME').sum().stack(future_stack=True).to_frame(name='volume')
        monthly_ret = monthly_close.unstack()['close'].ffill().pct_change().stack(future_stack=True).to_frame(name='r')

        long_monthly = pd.merge(monthly_vol, monthly_ret, how='inner', left_index=True, right_index=True)
        long_monthly = pd.merge(long_monthly, monthly_close, how='inner', left_index=True, right_index=True)
        long_monthly['yearReport'] = long_monthly.index.get_level_values(0).year
        long_monthly['lengthReport'] = long_monthly.index.get_level_values(0).quarter

        long_monthly = long_monthly.loc[self.idx[self.start_time:, :], :]
        long_monthly = long_monthly.reset_index()

        long_monthly = pd.merge(long_monthly, self.fun_data, how='left', on=['ticker', 'yearReport', 'lengthReport'])
        long_monthly = pd.merge(long_monthly, self.benchmark, how='left', on=['time'])
        long_monthly['book_to_market'] = 1 / long_monthly['P/B']
        long_monthly['log_mcap'] = np.log(long_monthly['close']*long_monthly['Outstanding Share'])

        long_monthly = long_monthly.set_index(['time', 'ticker'])
        long_daily = long_daily.sort_index(level=0)
        
        return long_daily, long_monthly
    
    def get_transform_data(self): 
        return self.__transform_data()    