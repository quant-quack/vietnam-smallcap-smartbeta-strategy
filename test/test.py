import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

class Crawler:     
    def __init__(self):
        self.table_list = [] 
        self.__driver_config() 
        self.driver = webdriver.Chrome(options=self.options)
        
    def __driver_config(self): 
        # Configure Chrome
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--start-maximized")
        self.options.page_load_strategy = 'eager'        
        
    def __accept_term(self): 
        # Navigate to url
        self.driver.get("https://www.dragoncapital.com/vef/")

        # Find Accept button
        accept_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#popmake-4108 > button")))
        accept_btn.click()

    def __get_table_data(self): 
        table = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#performance > div:nth-child(4) > table.bg-negative.stackcolumns.stacktable.large-only")))  
        tmp_table = pd.read_html(table.get_attribute("outerHTML"))
        
        self.table_list.append(tmp_table[0])
                    
    def crawl_benchmark_data(self): 
        try:
            # Login into Vietstock
            self.__accept_term() 
            
            # Wait for 5 second
            time.sleep(5)
            
            # Get table data
            self.__get_table_data()
            
            concat_table.to_csv("../data/benchmark/dc_performance.csv", index=False, header=1)
                
        finally: 
            self.driver.quit()

crawler = Crawler()
crawler.crawl_benchmark_data()