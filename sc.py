import os
import dotenv

# for scraper
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests

dotenv.load_dotenv()

class PhantomJSCloudClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = f'https://phantomjscloud.com/api/browser/v2/{api_key}/'

    def get_page_content(self, url):
        payload = {
            'url': url,
            'renderType': 'html'
        }
        response = requests.post(self.endpoint, json=payload)
        return response.text
    
class AmazonScraper():
    def scrape(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8'
        print(response.text)
        return response.text

    def get_price(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        print(soup)
        price_tag = soup.find('div', {'id': 'rightCol'})
        print(price_tag)
        return price_tag.get_text() if price_tag else None
    
class WalmartScraper():
    def scrape(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8'
        print(response.text)
        return response.text

    def get_price(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        print(soup)
        price_tag = soup.find('div', {'class': 'flex buy-box-container ba b--transparent br3 pa3 flex-column h-100'}) #.find('span', {'class': 'inline-flex flex-column'})
        print(price_tag)
        return price_tag.get_text() if price_tag else None

if __name__ == "__main__":
    url = 'https://www.walmart.com/ip/Birdie-Bath-Portable-Golf-Ball-Cleaner-Ultimate-Personal-Golf-Ball-Washer/3181856204?adsRedirect=true'
#    url = 'https://www.amazon.com/ELEMENT-Element14-Raspberry-Pi-Motherboard/dp/B07P4LSDYV'
    scraper = WalmartScraper()
    api_key = os.getenv('PhantomJsCloud_API_KEY')
    client = PhantomJSCloudClient(api_key)
#    response = scraper.scrape(url)
    response = client.get_page_content(url)
    print(response)
    scraper.get_price(response)