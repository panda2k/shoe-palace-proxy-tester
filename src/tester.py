from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, UnexpectedAlertPresentException
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import datetime
from itertools import chain
import concurrent.futures
import string
import os
import time

DRIVER_PATH = os.path.join(os.getcwd(), 'utils\\geckodriver.exe')
PROXY_LIST = os.path.join(os.getcwd(), 'utils\\proxylist.txt')

def get_driver(proxy = None): 
    options = Options()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0")
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    profile.set_preference("permissions.default.image", 2)
    options.headless = True
    return webdriver.Firefox(executable_path = DRIVER_PATH, options = options, firefox_profile = profile)

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

def log_to_file(log_file_path, message):
    with open(log_file_path, 'a') as f:
        f.write(message + '\n')
    
    return

def test_proxies(output_path, thread_name, log_path):
    print(f'Thread {str(thread_name)} started')
    driver = get_driver()
    print(f'Thread {str(thread_name)} got driver')
    while True:
        try:
            proxy = next(proxies)
            print(f'Thread {str(thread_name)} is now testing {proxy}')
            start_time = time.time()
        except StopIteration:
            driver.quit()
            return f'Thread {str(thread_name)} is done testing proxies'
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
                if 'proxyConnectFailure' in str(e):
                    test_data['result'].append('Dead')
                elif 'about:neterror' in str(e):
                    test_data['result'].append('Dead')
                elif 'Timeout' in str(e):
                    test_data['result'].append('Dead')
                else:
                    test_data['result'].append('Unknown')
                    driver.save_screenshot(os.path.join(os.getcwd(), f'logs\\{proxy.split(":")[1]}.png')) # optional debug
                    log_to_file(log_path, 'Proxy {}: {}'.format(proxy.split(":")[1], str(e))) # optional debug
            else:
                try:
                    if '501 Backend Timeout' in driver.page_source:
                        test_data['result'].append('501')
                    else:
                        try:
                            driver.find_element_by_id('cf-wrapper')
                            test_data['result'].append('Bad')
                        except NoSuchElementException:
                            test_data['result'].append('Good')
                except UnexpectedAlertPresentException:
                    test_data['result'].append('Auth error')
    
            dataframe = pd.DataFrame(test_data)
            dataframe.to_csv(output_path, index = False, mode = 'a', header = False)
            print(f'Thread {str(thread_name)} has finished testing {proxy}. Results of test: {test_data["result"][-1]}. Took {round(time.time() - start_time, 3)} seconds.')

def main():
    global proxies
    proxies = chain(load_proxies())
    TEST_PATH = os.path.join(os.getcwd(), 'tests\\' + datetime.now().strftime('%Y:%m:%d:%H:%M:%S').replace(':', '-') + '.csv')
    LOG_PATH = os.path.join(os.getcwd(), f"logs\\{datetime.now().strftime('%Y:%m:%d:%H:%M:%S').replace(':', '-') + '.txt'}")
    thread_count = int(input("How many threads would you like to run? "))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for index in range(thread_count):
            futures.append(executor.submit(test_proxies, TEST_PATH, index, LOG_PATH))
    for future in futures:
        print(future.result())
        
    print('All threads exited. Stopping program')


if __name__ == "__main__":
    main()
