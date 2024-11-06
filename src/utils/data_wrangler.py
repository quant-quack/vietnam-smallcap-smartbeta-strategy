import pandas as pd
import dask.dataframe as dd
import numpy as np
from glob import glob

class Wrangler: 
    def __init__(self, benchmark_dir, fundamental_csv_dir, historic_csv_dir, gics_csv_dir): 
        self.benchmark_dir = benchmark_dir
        self.fundamental_csv_dir = fundamental_csv_dir
        self.historic_csv_dir = historic_csv_dir
        self.gics_csv_dir = gics_csv_dir


    def __process_benchmark_data(self): 
        df = pd.read_csv(self.benchmark_dir, header=1, index_col=0)
        df = df.drop(columns='YTD')
        df.index = df.index.astype("int16")
        df = df.div(100)
        
        return df
    
    def __process_sector_data(self): 
        # Get the symbol available in daily data
        historical_csv_files = glob(self.historic_csv_dir + '*.csv')
        sector_info = pd.read_csv(self.gics_csv_dir)
        
        available_universe = [file[-7:-4] for file in historical_csv_files]
        
        # Drop rows with nan value in sector field
        sector_info = sector_info.dropna(subset=['sector'])
        
        # Sector mask for current daily symbols
        mask_available_universe = sector_info['ticker'].isin(available_universe)
        universe_sector_info = sector_info[mask_available_universe]
        
        # Mapping Sector
        sector_mapping = {
            'Financials': ['Bảo hiểm', 'Dịch vụ tài chính', 'Tổ chức tín dụng'],
            'Information Technology': ['Chất bán dẫn và thiết bị bán dẫn', 'Công nghệ phần cứng và thiết bị', 'Phần mềm và dịch vụ'],
            'Health Care': ['Dược phẩm, Công nghệ sinh học và Khoa học thường thức', 'Dịch vụ và thiết bị chăm sóc sức khỏe'],
            'Consumer Discretionary': ['Dịch vụ tiêu dùng', 'Hàng tiêu dùng và trang trí', 'Phân phối và bán lẻ hàng lâu bền', 'Xe và linh kiện', 'Đồ gia dụng và cá nhân'],
            'Utilities': ['Dịch vụ tiện ích'],
            'Communication Services': ['Dịch vụ viễn thông', 'Truyền thông và giải trí'],
            'Materials': ['Nguyên vật liệu'],
            'Energy': ['Năng lượng'],
            'Real Estate': ['Phát triển và quản lý bất động sản'],
            'Consumer Staples': ['Thực phẩm, đồ uống và thuốc lá'],
            'Industrials': ['Dịch vụ chuyên biệt và thương mại', 'Tư liệu sản xuất', 'Vận tải']
        }
        
        # Reverse sector_mapping 
        industry_to_sector = {industry: sector for sector, industries in sector_mapping.items() 
                                               for industry in industries}
        mapped_sector = universe_sector_info['sector'].map(industry_to_sector)

        # Add new Sector column based on sector_mapping
        universe_sector_info.loc[:, ['mapped sector']] = mapped_sector.values

        # Rename 'Sector' and 'Mapped Sector' columns
        universe_sector_info = universe_sector_info.rename(columns={
                            'sector': 'industry groups',
                            'mapped sector': 'sector'
                            })
        # Reset index
        universe_sector_info.reset_index(drop=True, inplace=True)
        
        return universe_sector_info

    def __find_symbol_enough_data_field(self):  
        files = glob(self.fundamental_csv_dir + '*.csv')
            
        not_enough_field = []
        validate_col = set(['P/B', 'Market Capital', 'Outstanding Share'])

        for file in files:
            df = pd.read_csv(file)

            if not validate_col.issubset(set(df.columns)):
                not_enough_field.append(file)

        valid_symbol = set(files).difference(not_enough_field)
        
        return valid_symbol
    
    def __define_universe(self, exclude_finsector): 
        # Filter out symbols that have enough data fields
        symbol_enough_field = self.get_symbol_enough_data_field()
        enough_field_symbols = [symbol[-7:-4] for symbol in symbol_enough_field]
        
        sector_info = self.get_processed_sector_data()
        
        if exclude_finsector: 
            mask_non_financial_sector = sector_info['sector'] != 'Financials'
            remain_sector = set(sector_info[mask_non_financial_sector]['ticker'])
        else: 
            remain_sector = set(sector_info['ticker'])
        
        universe = remain_sector.intersection(enough_field_symbols)

        return universe
    
    def __map_fundamental_data(self, df): 
        fields = ['ticker', 'yearReport', 'lengthReport', 'P/B','Outstanding Share']
    
        df = df.sort_values(by=['yearReport', 'lengthReport'])
        df = df.replace(to_replace=0, value=np.nan).bfill()
        
        return df[fields]
    
    def __map_drop_duplicate_date(self, df): 
        df = df.drop_duplicates(subset='time', keep='first')
        
        return df
    
    def __process_historical_data(self, exclude_finsector): 
        universe_historical_dir = [self.historic_csv_dir + f'{symbol}.csv' for symbol in self.__define_universe(exclude_finsector)]
        
        historical_data = dd.read_csv(universe_historical_dir)
        
        historical_data = historical_data.map_partitions(self.__map_drop_duplicate_date)
        historical_data['time'] = dd.to_datetime(historical_data['time'])
        historical_data['yearReport'] = historical_data['time'].dt.year
        historical_data['lengthReport'] = historical_data['time'].dt.quarter
        processed_historical_data = historical_data.compute()
        processed_historical_data = processed_historical_data.reset_index(drop=True)
        
        return processed_historical_data
            
    def __process_fundamental_data(self, exclude_finsector): 
        universe_fundmental_dir = [self.fundamental_csv_dir + f'{symbol}.csv' for symbol in self.__define_universe(exclude_finsector)]
        
        fundamental_data = dd.read_csv(universe_fundmental_dir)
        
        meta = pd.DataFrame({
                             'ticker': pd.Series(dtype='string'),
                             'yearReport': pd.Series(dtype='int16'),
                             'lengthReport': pd.Series(dtype='int16'),
                             'P/B': pd.Series(dtype='float64'),
                             'Outstanding Share': pd.Series(dtype='int64')
                            })

        fundamental_data = fundamental_data.map_partitions(self.__map_fundamental_data, meta=meta)
        processed_fundamental_data = fundamental_data.compute(assume_missing=True) 
        processed_fundamental_data = processed_fundamental_data.reset_index(drop=True)
        
        return processed_fundamental_data
        
    def get_processed_sector_data(self): 
        return self.__process_sector_data()
    
    def get_symbol_enough_data_field(self): 
        return self.__find_symbol_enough_data_field()
    
    def get_benchmark_data(self):
        return self.__process_benchmark_data()
    
    def get_universe(self, exclude_finsector=True): 
        return self.__define_universe(exclude_finsector)
    
    def get_processed_historical_data(self, exclude_finsector=True): 
        return self.__process_historical_data(exclude_finsector) 
    
    def get_processed_fundamental_data(self, exclude_finsector=True): 
        return self.__process_fundamental_data(exclude_finsector)






