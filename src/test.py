import pandas as pd

from glob import glob

import concurrent.futures
import time
import logging
from vnstock3 import Vnstock

def get_listing_info(stock, asset_type='STOCK', exchange=None):
    listing = stock.listing.symbols_by_exchange()
    mask = True
    
    # Filter out asset types that are stocks
    mask_type = listing['type'] == asset_type
    mask &= mask_type
    
    # Filter stocks based on listing exchange
    if exchange != None: 
        mask_exchange = listing['exchange'] == exchange
        mask &= mask_exchange
    
    listing_info = listing[mask]

    return listing_info

# Hàm để lấy dữ liệu với xử lý logic Exponential Backoff
def get_historical_data(stock, symbol, start, end, interval='1D', max_retries=10, initial_delay=2):  
    retries = 0  # Số lần thử lại
    while retries <= max_retries:
        try:
            print(f'Processing: {symbol} ...')
            tmp = stock.quote.history(symbol=symbol, start=start, end=end, interval=interval)
            tmp['ticker'] = symbol                
            tmp.to_csv(f'../data/historical_data/{symbol}.csv', index=False)
            print(f'Successfully processed {symbol}')
            return symbol  # Trả về symbol khi thành công
        except Exception as e:
            # Check for error 429 - Too Many Requests
            if '429' in str(e):
                retries += 1
                if retries <= max_retries:
                    wait_time = initial_delay * (2 ** (retries - 1))  # Tăng dần thời gian chờ
                    print(f"Too Many Requests for {symbol}. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to process {symbol} after {max_retries} retries.")
                    return None  # Thất bại sau quá nhiều retries
            else:
                # Handle other exceptions
                print(f"Error processing {symbol}: {e}")
                return None

# Hàm lấy dữ liệu song song
def fetch_all_symbols(stock, symbols, start, end, interval):
    results = []
    max_workers = 8  # Giới hạn số lượng yêu cầu song song

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {executor.submit(get_historical_data, stock, symbol, start, end, interval): symbol for symbol in symbols}

        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as exc:
                print(f"{symbol} generated an exception: {exc}")
    
    return results

if __name__ == '__main__':
    start = '2002-01-01'
    end = '2023-12-31'
    interval = '1D'
    source = 'tcbs'
    
    # Initialize instance for Vnstock
    stock = Vnstock().stock(symbol='VNINDEX', source=source)
    
    # Get listing information
    df = get_listing_info(stock)
    total_symbol = set(df.symbol.values)
    mask_delisted = df['exchange'] == 'DELISTED'
    delisted_symbol = set(df[mask_delisted].symbol)
    listed_symbol = total_symbol.difference(delisted_symbol)
    
    print(f"\nTotal symbols: {len(total_symbol)}")
    print(f"Delisted symbols: {len(delisted_symbol)}")
    print(f"Listed symbols: {len(listed_symbol)}\n")

    # Retrieve historical data
    historical_file_retrieve = glob('../data/historical_data/*.csv')
    complete_retrieved = [file[-7:-4] for file in historical_file_retrieve]
    inprogress_retrieved = total_symbol.difference(complete_retrieved)
    
    print(f"Retrieving data for {len(inprogress_retrieved)} symbols...")

    # Fetch data for all symbols
    results = fetch_all_symbols(stock, inprogress_retrieved, start=start, end=end, interval=interval)
    
    print(f"Completed fetching data for {len(results)} symbols.")
