import pandas as pd
from io import StringIO
from alive_progress import alive_bar
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GicsCrawler:     
    def __init__(self):
        self.email = 'gbn20668@dcobe.com'
        self.password = '123456'
        self.driver = self.__setup_driver() 
        
    def __setup_driver(self): 
        # Configure Chrome
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--start-maximized")
        self.options.page_load_strategy = 'eager' 
        
        return webdriver.Chrome(options=self.options)       
        
    def __login(self): 
        # Navigate to url
        self.driver.get("https://finance.vietstock.vn/doanh-nghiep-a-z?page=1")

        # Find loggin button
        loggin_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "body > div.page-container > div.hidden-sm.hidden-xs > div.container > div.navbar-collapse.collapse.no-padder > div > a.title-link.btnlogin-link")))
        loggin_btn.click()

        # Fill in login information
        self.driver.find_element(by=By.CSS_SELECTOR, value="#txtEmailLogin").send_keys(self.email)
        self.driver.find_element(by=By.CSS_SELECTOR, value="#txtPassword").send_keys(self.password)
        self.driver.find_element(by=By.CSS_SELECTOR, value="#btnLoginAccount").click()

    def __get_all_pages_data(self): 
        # Select 50 entries per page
        select_menu = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#az-container > div:nth-child(1) > div.pull-right > div > select")))
        Select(select_menu).select_by_value("50")
        
        # Retrieve the total page count
        pages_elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[17]/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/span[1]/span[2]")))
        total_page = int(pages_elem.text)
        
        table_dfs = []
        
        print("Scrapping GICS data ...")
        with alive_bar(total_page) as bar: 
            while True: 
                table = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#az-container > div.table-responsive.clear-fix.no-m-b > table")))  
                table_dfs.append(pd.read_html(StringIO(table.get_attribute("outerHTML")))[0])

                # Check if the next button is disabled
                try: 
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "#btn-page-next")
                    if not next_btn.is_enabled(): 
                        break # Exit loop if no more pages
                    next_btn.click()
                except: 
                    break # Exit loop if the button is not found
                
                bar()
                
        return pd.concat(table_dfs, axis=0)
            
    def crawl_gics_data(self): 
        try:
            # Login into Vietstock
            self.__login() 
            
            time.sleep(6)
            
            # Get all table data
            gics_data = self.__get_all_pages_data()
            
            if gics_data.shape[0] == 3325: 
                gics_data.to_csv("../data/gics/gics.csv", index=False)
                print(f"Data successfully crawled for {gics_data.shape[0]} symbol.")
                
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
        
        return pd.read_html(StringIO(table.get_attribute("outerHTML")))[0]
            
    def crawl_benchmark_data(self): 
        try:
            table_data = self.__accept_and_collect_table()   
            table_data.to_csv('../data/benchmark/dc_performance.csv')
            print("Benchmark data crawling complete.")             
        finally: 
            self.driver.quit()