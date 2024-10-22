import pandas as pd

import time
from glob import glob
import shutil
import logging
import concurrent.futures

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
        
def get_fundamental_data(symbol, max_retries=10, initial_delay=2):    
    retries = 0  # Count the number of retries for each symbol
    while retries <= max_retries:
        try:
            print(f'Processing: {symbol}')
            stock = Vnstock().stock(symbol=symbol, source=source)                
            tmp = stock.finance.ratio(period='quarter').droplevel(0, axis=1)
            mapper = {
                'Market Capital (Bn. VND)': 'Market Capital', 
                'Outstanding Share (Mil. Shares)': 'Outstanding Share' 
            }
            tmp.rename(columns=mapper, inplace=True)
            tmp.reset_index(drop=True, inplace=True)   
            tmp.iloc[2:, :6]
            tmp.to_csv(f'../data/fundamental_data/{symbol}.csv', index=False)
            return symbol  # If successful, return symbol
        
        except Exception as e:
            # Check for error 429 - Too Many Requests
            if '429' in str(e):
                retries += 1
                if retries <= max_retries:
                    wait_time = initial_delay * (2 ** (retries - 1))  # Double the wait time for each retry
                    print(f"Too Many Requests for {symbol}. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to process {symbol} after {max_retries} retries.")
                    return None
            else:
                # Handle other exceptions
                print(f"Error processing {symbol}: {e}")
                
                return None

def fetch_all_symbols(stock, symbols): 
    results = [] # List used to store retrieved results
    max_workers = 8 # Maximum number of threads used 
    
    # Use ThreadPool to fetch data
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor: 
        future_to_symbol = {executor.submit(get_fundamental_data, symbol): symbol for symbol in symbols} # Initialize placeholder for symbols
        
        for future in concurrent.futures.as_completed(future_to_symbol): 
            # Try to get the result from the placeholder, if not raise an error
            symbol = future_to_symbol[future]
            try:
                result = future.result() 
                if result: 
                    results.append(result)
            except Exception as exc: 
                print(f"{symbol} generated error: {exc}")            

    return results

if __name__ == '__main__': 
    
    source='vci'

    # Initialize instance for Vnstock
    data_explore_logger = logging.getLogger(f'vnstock3.common.data.data_explorer')
    data_explore_logger.setLevel(logging.CRITICAL)  # Set log level highher than WARNING level  
    
    stock = Vnstock().stock(symbol='VNINDEX', source=source)
    
    # Get listiyeestinformation summary
    df = get_listing_info(stock)
    total_symbol = set(df.symbol.values)
    mask_delisted = df['exchange'] == 'DELISTED'
    delisted_symbol = set(df[mask_delisted].symbol)
    listed_symbol = total_symbol.difference(delisted_symbol)
    print("\nListing information summary:")
    print("Total symbol: ", len(total_symbol))
    print("Total number of companies delisted on the three exchanges: ", len(delisted_symbol))
    print("Total number of companies listed on the three exchanges: ", len(listed_symbol))
    print()
    
    # Retrieve fundamental data
    fundamental_file_retrive = glob('../data/fundamental_data/*.csv')
    complete_retrieved = [file[-7:-4] for file in fundamental_file_retrive]
    inprogress_retrieved = total_symbol.difference(complete_retrieved)
    
    print(f"Retrieving data for {len(inprogress_retrieved)} symbols...")
    
    # Fetch data for all symbols
    results = fetch_all_symbols(stock=stock, symbols=inprogress_retrieved)
    
    print(f"Complete fetching data for {len(results)} symbols.")