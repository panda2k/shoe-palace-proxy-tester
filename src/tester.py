from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import os
import time

DRIVER_PATH = os.path.join(os.getcwd(), 'utils\\geckodriver.exe')
PROXY_LIST = os.path.join(os.getcwd(), 'utils\\proxylist.txt')

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

proxies = load_proxies()

for proxy in proxies:
    driver = proxy_driver(proxy)
    driver.get('https://www.shoepalace.com/')
    try:
        driver.find_element_by_id('cf-wrapper')
        print(proxy.replace('\n', '') + ' bad')
    except NoSuchElementException:
        print(proxy.replace('\n', '') + ' good')
    time.sleep(3)
    driver.quit()
