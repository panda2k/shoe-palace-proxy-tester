from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import datetime
import os
import time

DRIVER_PATH = os.path.join(os.getcwd(), 'utils\\geckodriver.exe')
PROXY_LIST = os.path.join(os.getcwd(), 'utils\\proxylist.txt')
TEST_PATH = os.path.join(os.getcwd(), 'tests\\' + datetime.now().strftime('%Y:%m:%d:%H:%M:%S').replace(':', '-') + '.csv')

def proxy_driver(proxy): 
    desired_capability = webdriver.DesiredCapabilities.FIREFOX

    desired_capability['proxy'] = {
        "proxyType":"manual",
        "httpProxy": proxy,
        "sslProxy": proxy,
    }
    options = Options()
    #options.headless = True
    return webdriver.Firefox(executable_path = DRIVER_PATH, capabilities = desired_capability, options = options)

def load_proxies():
    with open(PROXY_LIST, 'r') as f:
        return f.readlines()

def main():
    proxies = load_proxies()
    test_data = {
        'proxy': [],
        'result': [],
    }

    for proxy in proxies:
        driver = proxy_driver(proxy)
        driver.get('https://www.shoepalace.com/')
        test_data['proxy'].append(proxy)
        try:
            driver.find_element_by_id('cf-wrapper')
            test_data['result'].append('Bad')
        except NoSuchElementException:
            test_data['result'].append('Good')
        
        driver.quit()
    
    dataframe = pd.DataFrame(test_data)
    dataframe.to_csv(TEST_PATH, index = False)

if __name__ == "__main__":
    main()
