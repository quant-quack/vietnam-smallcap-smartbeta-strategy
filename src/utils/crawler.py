import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

class GicsCrawler:     
    def __init__(self):
        self.table_dfs = [] 
        self.email = 'gbn20668@dcobe.com'
        self.password = '123456'
        self.__driver_config() 
        self.driver = webdriver.Chrome(options=self.options)
        
    def __driver_config(self): 
        # Configure Chrome
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--start-maximized")
        self.options.page_load_strategy = 'eager'        
        
    def __login(self): 
        # Navigate to url
        self.driver.get("https://finance.vietstock.vn/doanh-nghiep-a-z?page=1")

        # Find loggin button
        loggin_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "body > div.page-container > div.hidden-sm.hidden-xs > div.container > div.navbar-collapse.collapse.no-padder > div > a.title-link.btnlogin-link")))
        loggin_btn.click()

        # Fill in login information
        email_field = self.driver.find_element(by=By.CSS_SELECTOR, value="#txtEmailLogin")
        password_field = self.driver.find_element(by=By.CSS_SELECTOR, value="#txtPassword")

        email_field.send_keys(self.email)
        password_field.send_keys(self.password)
        
        submit_btn = self.driver.find_element(by=By.CSS_SELECTOR, value="#btnLoginAccount")
        submit_btn.click()

    def __get_table_data(self): 
        select_menu = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#az-container > div:nth-child(1) > div.pull-right > div > select")))
        Select(select_menu).select_by_value("50")

        table = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#az-container > div.table-responsive.clear-fix.no-m-b > table")))  
        tmp_table = pd.read_html(table.get_attribute("outerHTML"))
        
        self.table_dfs.append(tmp_table[0])

        for i in range(65):
            next_btn = self.driver.find_element(By.CSS_SELECTOR, "#btn-page-next")
            next_btn.click()
            next_table = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#az-container > div.table-responsive.clear-fix.no-m-b > table")))  
            tmp_table = pd.read_html(next_table.get_attribute("outerHTML"))
            self.table_dfs.append(tmp_table[0])
            
    def crawl_gics_data(self): 
        try:
            # Login into Vietstock
            self.__login() 
            
            # Wait for 5 second
            time.sleep(5)
            
            # Get table data
            self.__get_table_data()
            
            # Concatenate the results
            concat_table = pd.concat(self.table_dfs, axis=0)
            
            if concat_table.shape[0] == 3275: 
                concat_table.to_csv("../data/gics/gics.csv", index=False)
                print(f"Complete crawling data for {concat_table.shape[0]}. ")
                
        finally: 
            self.driver.quit()

class BenchmarkCrawler:     
    def __init__(self):
        self.driver = self.__setup_driver()
        
    def __setup_driver(self): 
        # Configure Chrome
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--start-maximized")
        self.options.page_load_strategy = 'eager'
        
        return webdriver.Chrome(options=self.options)    
        
    def __accept_and_collect_table(self): 
        # Navigate to url
        self.driver.get("https://www.dragoncapital.com/vef/")

        # Find Accept button
        accept_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#popmake-4108 > button")))
        accept_btn.click()
        
        table = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#performance > div:nth-child(4) > table.bg-negative.stackcolumns.stacktable.large-only")))  
        
        return pd.read_html(table.get_attribute("outerHTML"))[0]
            
    def crawl_benchmark_data(self): 
        try:
            table_data = self.__accept_and_collect_table()   
            table_data.to_csv('../data/benchmark/dc_performance.csv')             
        finally: 
            self.driver.quit()