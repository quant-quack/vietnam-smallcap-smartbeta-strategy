from utils.market_data_fetcher import * 
from utils.crawler import GicsCrawler, BenchmarkCrawler


from glob import glob
import time
import shutil
import logging

from vnstock3 import Vnstock


if __name__ == '__main__': 
    
    start='2002-01-01'
    end='2023-12-31'
    interval='1D'
    symbol='VNINDEX'
    source='VCI'



    # Initialize instance for Vnstock
    data_explore_logger = logging.getLogger(f'vnstock3.common.data.data_explorer')
    data_explore_logger.setLevel(logging.CRITICAL)  # Set log level highher than WARNING level  
    
    stock = Vnstock().stock(symbol='VNINDEX', source=source)
    
    # Get listing information summary
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
    
    # RETRIEVE HISTORICAL DATA
    historical_file_retrieve = glob('../data/historical_data/*.csv')
    complete_retrieved = [file[-7:-4] for file in historical_file_retrieve]
    inprogress_retrieved = total_symbol.difference(complete_retrieved)
    
    print(f"Retrieving historical data for {len(inprogress_retrieved)} symbols...")
    # Fetch historical data for all symbols
    results = fetch_all_symbols(stock=stock, source=source, symbols=inprogress_retrieved, start=start, end=end, interval=interval,fetch_type='historical')
    print(f"Complete fetching data for {len(results)} symbols.")
    print() 
    
    # RETRIEVE FUNDAMENTAL DATA
    fundamental_file_retrive = glob('../data/fundamental_data/*.csv')
    complete_retrieved = [file[-7:-4] for file in fundamental_file_retrive]
    inprogress_retrieved = total_symbol.difference(complete_retrieved)
    
    print(f"Retrieving fundamental data for {len(inprogress_retrieved)} symbols...")
    # Fetch fundamental data for all symbols
    results = fetch_all_symbols(stock=stock, source=source, symbols=inprogress_retrieved, start=start, end=end, interval=interval,fetch_type='fundamental')
    print(f"Complete fetching data for {len(results)} symbols.")
    print()
    
    # RETRIEVE GICS DATA
    gics_crawler = GicsCrawler()
    gics_crawler.crawl_gics_data()
    print()
    
    # RETRIEVE BENCHMARK DATA
    benchmark_crawler = BenchmarkCrawler()
    benchmark_crawler.crawl_benchmark_data()
    
    
    
    