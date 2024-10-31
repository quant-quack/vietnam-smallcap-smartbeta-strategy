import pandas as pd
import numpy as np
from glob import glob

def process_sector_data(sector_info: pd.DataFrame): 
    # Get the symbol available in daily data
    files = glob('../data/fundamental_data/*.csv')
    available_daily_symbol = [file[-7:-4] for file in files]
    
    # Drop unnecessary columns
    sector_info = sector_info.drop(columns=['STT', 'Tên công ty'])
    sector_info = sector_info.rename(columns={
                                              'Mã CK▲': 'ticker',
                                              'Ngành': 'sector',
                                              'Sàn': 'exchange',
                                              'Khối lượng NY/ĐKGD': 'volume of listed'
                                            })
                                    
    # Drop symbol whose sectors are NaN
    sector_info.dropna(subset=['sector'], inplace=True)
    
    # Sector mask for current daily symbols
    mask_daily_universe = sector_info['ticker'].isin(available_daily_symbol)
    daily_universe = sector_info[mask_daily_universe]
    
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
    industry_to_sector = {industry: sector for sector, industries in sector_mapping.items() for industry in industries}
    mapped_sector = daily_universe['sector'].map(industry_to_sector)

    # Add new Sector column based on sector_mapping
    daily_universe.loc[:, ['mapped sector']] = mapped_sector.values

    # Rename 'Sector' and 'Mapped Sector' columns
    daily_universe = daily_universe.rename(columns={
                         'sector': 'industry groups',
                         'mapped sector': 'sector'
                         })
    # Reset index
    daily_universe.reset_index(drop=True, inplace=True)
    
    return daily_universe

def find_symbol_enough_field(files):      
    not_enough_field = []
    validate_col = set(['P/B', 'Market Capital', 'Outstanding Share'])

    for file in files:
        df = pd.read_csv(file)

        if not validate_col.issubset(set(df.columns)):
            not_enough_field.append(file)

    valid_symbol = set(files).difference(not_enough_field)
    
    return valid_symbol

def process_fundamental_data(df: pd.DataFrame):
    fields = ['symbol', 'yearReport', 'lengthReport', 'P/B','Outstanding Share']
    
    df = df.sort_values(by=['yearReport', 'lengthReport'])
    df = df.replace(to_replace=0, value=np.nan).bfill()
    
    return df[fields]


def get_risk_free_rate(file):     
    df = pd.read_csv(file)
    df.rename(columns={
                      'Date': 'time',
                      'Close': 'rf',
                      'Open': 'open',
                      'High': 'high',
                      'Low': 'low'
                      },
              inplace=True
    )
    df.drop(columns=['open', 'high', 'low','Change %'], inplace=True)
    
#     df['rf'] = np.exp(df['rf'] / 250) - 1
        
    df['time'] = pd.to_datetime(df['time'])
    
    return df

def get_enough_data_folder(fundamental_path, historical_path, symbols): 
    fundamental_folder = [fundamental_path + f'/{symbol}.csv' for symbol in symbols]
    historical_folder = [historical_path + f'/{symbol}.csv' for symbol in symbols]
    
    return fundamental_folder, historical_folder

def get_enough_data_folder(fundamental_path, historical_path, symbols): 
    fundamental_folder = [fundamental_path + f'/{symbol}.csv' for symbol in symbols]
    historical_folder = [historical_path + f'/{symbol}.csv' for symbol in symbols]
    
    return fundamental_folder, historical_folder

def drop_duplicate_date(df): 
    df = df.drop_duplicates(subset='time', keep='first')
    
    return df


def get_universe(): 
    files = glob('/kaggle/input/vn-equities-ver6/vn-equities-ver6/fundamental_data/*.csv')
    sector_info = pd.read_csv('/kaggle/input/vn-equities-ver6/vn-equities-ver6/GICS.csv')

    # Filter out symbols that have enough data fields
    symbol_enough_field = find_symbol_enough_field(files)
    enough_field_symbols = [symbol[-7:-4] for symbol in symbol_enough_field]
    
    sector_info = process_sector_data(sector_info)
    mask_non_financial_sector = sector_info['Sector'] != 'Financials'
    
    non_financial_sector = set(sector_info[mask_non_financial_sector]['Symbol'])
    universe = non_financial_sector.intersection(enough_field_symbols)

    return universe