from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import argparse
import csv

def getURL(query):
    return f'https://www.nasdaq.com/market-activity/stocks/{query}/historical?page=1&rows_per_page=10&timeline=y10'

def download(driver, query):
    url = getURL(query)
    driver.get(url)
    try:
        download_button =  WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'historical-download')))
        download_button.click()
    except NoSuchElementException:
        print('No download button, skipping')
    except TimeoutException:
        print('Timeout Exception, skipping')
    time.sleep(1)

def newChromeBrowser(index, ticker):
    options = Options()
    if not os.path.exists(f'historical-data-f/{index}_{ticker}'):
                os.makedirs(f'historical-data-f/{index}_{ticker}')
    prefs = {'download.default_directory': os.path.abspath(f'historical-data-f/{index}_{ticker}')}
    options.add_experimental_option('prefs', prefs)
    browser = Chrome(options=options)
    return browser


def loop(file, col):
    with open(file, 'r') as fileobj:
        ticker_list = csv.reader(fileobj)
        print(ticker_list)

        num = 236
        for index, tickers in enumerate(ticker_list):
            if index == 0:
                    continue
            ticker = tickers[col]
            safe_ticker = ticker.replace('/', '.')
            driver = newChromeBrowser(num, safe_ticker)
            download(driver, safe_ticker)
            driver.quit
            num += 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--csv_file", type=str, required=True)
    parser.add_argument("-i", "--list", type=int, required=True)
    args = parser.parse_args()
    file = f'{args.csv_file}.csv'
    print(file)
    if not os.path.exists("historical-data-f"):
        os.makedirs("historical-data-f")
    loop(file, args.list)
            

    
if __name__ == "__main__":
    main()