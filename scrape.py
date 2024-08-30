from datetime import datetime
import argparse
import csv
import requests
from bs4 import BeautifulSoup
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


DAYS_INTERVAL = 120
DAYS_BACK = 3650
class GoogleNewsFeedScraper:
    def __init__(self):
        self.data = []
        self.collected_dates = set()
        
    def convert_to_rss_url(self, query, page_number):
        return f'https://markets.businessinsider.com/news/{query}-stock?p={page_number}'
    
    def scrape_google_news_feed(self, query, file):
        ##s = Service('../chromedriver_linux64/chromedriver.exe')
        ##options = Options()
        ##options.add_argument("start-maximized")
        ##options.add_argument("--disable-blink-features=AutomationControlled")
        ##options.add_experimental_option("excludeSwitches", ["enable-automation"])
        ##driver = webdriver.Chrome(service=s, options=options)
        page_number = 1
        while True:
            converted_url = self.convert_to_rss_url(query, page_number)
            response = requests.get(converted_url)
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            articles = soup.find_all('div', class_= 'latest-news__story')

            if not articles:
                self.data = []
                self.collected_dates = set()
                break

            for article in articles:
                title = article.find('a', class_= "news-link").text
                pubdate = article.find('time', class_ = 'latest-news__date').get('datetime')
                pubdate_dt = datetime.strptime(pubdate, '%m/%d/%Y %I:%M:%S %p').date()
                if pubdate_dt not in self.collected_dates:
                    self.data.append([query, title, pubdate])
                    self.collected_dates.add(pubdate_dt)
            
            with open(file, "w+", newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Ticker", "Title", "Link"])
                for row in self.data:
                    csv_writer.writerow(row)
            
            page_number += 1

    def loop_scraping(self, file, list):
        with open(file) as file_obj:
            ticker_list = csv.reader(file_obj)
            num = 1
            for index, tickers in enumerate(ticker_list):
                if index == 0:
                    continue
                ticker = tickers[0].split(",")[list]
                safe_ticker = ticker.replace('/', '_')
                file = f"Headlines/{num}_{safe_ticker}.csv"
                print(safe_ticker)
                self.scrape_google_news_feed(safe_ticker, file)
                num += 1

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--csv_file", type=str, required=True, help="Search query file for Google News")
    parser.add_argument("-i", "--list", type=int, required=True, help="Search query file for Google News")

    args = parser.parse_args()
    scraper = GoogleNewsFeedScraper()
    file = f'{args.csv_file}.csv'
    if not os.path.exists("Headlines"):
        os.makedirs("Headlines")
    scraper.loop_scraping(file, args.list)
            

    
if __name__ == "__main__":
    main()