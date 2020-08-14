from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import datetime
from itertools import chain
import concurrent.futures
import random
import string
import os
import time

DRIVER_PATH = os.path.join(os.getcwd(), 'utils\\geckodriver.exe')
PROXY_LIST = os.path.join(os.getcwd(), 'utils\\proxylist.txt')

def get_driver(proxy = None): 
    options = Options()
    #options.headless = True TODO: Figure out a headless implementation
    return webdriver.Firefox(executable_path = DRIVER_PATH, options = options)

def change_proxy(driver, proxy):
    with driver.context(driver.CONTEXT_CHROME):
        proxy_addr = proxy.split(':')[0]
        proxy_port = proxy.split(':')[1]
        driver.execute_script("""
        Services.prefs.setIntPref('network.proxy.type', 1);
        Services.prefs.setCharPref("network.proxy.http", arguments[0]);
        Services.prefs.setIntPref("network.proxy.http_port", arguments[1]);
        Services.prefs.setCharPref("network.proxy.ssl", arguments[2]);
        Services.prefs.setIntPref("network.proxy.ssl_port", arguments[3]);
        """, proxy_addr, proxy_port, proxy_addr, proxy_port)
        driver.execute("SET_CONTEXT", {"context": "content"})

def load_proxies():
    with open(PROXY_LIST, 'r') as f:
        return [line.rstrip('\n') for line in f]

def test_proxies(output_path, thread_name):
    print(f'Thread {str(thread_name)} started')
    driver = get_driver()
    print(f'Thread {str(thread_name)} got driver')
    while True:
        try:
            proxy = next(proxies)
            print(f'Thread {str(thread_name)} is now testing {proxy}')
        except StopIteration:
            print(f'Thread {str(thread_name)} is done testing proxies')
            driver.quit()
            return
        else:
            change_proxy(driver, proxy)
            driver.delete_all_cookies()
            test_data = {
                'proxy': [],
                'result': [],
            }
            test_data['proxy'].append(proxy)
            try:
                driver.get('https://www.shoepalace.com/')
            except WebDriverException as e:
                if 'proxyConnectFailure'in str(e):
                    test_data['result'].append('Dead')
                else:
                    test_data['result'].append('Unknown')
            else:
                time.sleep(0.1)
                if '501 Backend Timeout' in driver.page_source:
                    test_data['result'].append('501')
                else:
                    try:
                        driver.find_element_by_id('cf-wrapper')
                        test_data['result'].append('Bad')
                    except NoSuchElementException:
                        test_data['result'].append('Good')
    
            dataframe = pd.DataFrame(test_data)
            dataframe.to_csv(output_path, index = False, mode = 'a')
            print(f'Thread {str(thread_name)} has finished testing {proxy}')
            time.sleep(5)

def main():
    global proxies
    proxies = chain(load_proxies())
    TEST_PATH = os.path.join(os.getcwd(), 'tests\\' + datetime.now().strftime('%Y:%m:%d:%H:%M:%S').replace(':', '-') + '.csv')
    with concurrent.futures.ThreadPoolExecutor(max_workers = 3) as executor:
        for index in range(3):
            executor.submit(test_proxies, TEST_PATH, index)


if __name__ == "__main__":
    main()
