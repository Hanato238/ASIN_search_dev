import os
import dotenv

# for scraper
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests

# for DB
import pymysql
from google.cloud.sql.connector import Connector

dotenv.load_dotenv()


class DatabaseClient:
    def __init__(self, instance_connection_name, user, password, database):
        self.connector = Connector()
        self.connection = self.connector.connect(
            instance_connection_name,
            "pymysql",
            user=user,
            password=password,
            db=database
        )
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        print("connected to Cloud SQL")

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.connector.close()


class Repository:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_urls(self):
        query = 'SELECT id, ec_url FROM products_ec WHERE price IS NULL'
        return self.db_client.execute_query(query)
    
    def fill_db(self, price, id):
        query="""
            UPDATE products_ec 
            SET price = %s
            WHERE id = %s;
         """
        self.db_client.execute_update(query, (price, id))

class ScraperStrategy(ABC):
    @abstractmethod
    def scrape(self, url):
        pass

class ScraperStrategy(ABC):
    @abstractmethod
    def scrape(self, url):
        pass

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

class AmazonScraper(ScraperStrategy):
    def scrape(self, url):
        response = requests.get(url)
        print(response.text)
        return response.text

    def get_price(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        print(soup)
        price_tag = soup.find('div', {'id': 'rightCol'}).find('span', class_='a-offscreen')
        print(price_tag)
        return price_tag.get_text() if price_tag else None

class Main:
    def __init__(self, scraper: ScraperStrategy, url, client: PhantomJSCloudClient = None):
        self.scraper = scraper
        self.url = url
        self.client = client

    def run(self):
        if self.client:
            html_content = self.client.get_page_content(self.url)
        else:
            html_content = self.scraper.scrape(self.url)
        
        price = self.scraper.get_price(html_content)
        print(price)
        

class WalmartScraper(ScraperStrategy):
    def scrape(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('span', class_='item_name').get_text(strip=True)
        price = soup.find('span', class_='price').get_text(strip=True)
        return {"title": title, "price": price}

class EBayScraper(ScraperStrategy):
    def scrape(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='ProductTitle').get_text(strip=True)
        price = soup.find('span', class_='Price').get_text(strip=True)
        return {"title": title, "price": price}

class ScraperContext:
    def __init__(self, strategy: ScraperStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ScraperStrategy):
        self._strategy = strategy

    def scrape(self, url):
        return self._strategy.scrape(url)

def get_scraper(url):
    if "amazon.com" in url:
        return AmazonScraper()
    elif "walmart.com" in url:
        return WalmartScraper()
    elif "ebay.com" in url:
        return EBayScraper()
    else:
        raise ValueError("Unsupported site")

def create_DB_connection():
    db_config = {
        'instance_connection_name': os.getenv('INSTANCE_CONNECTION_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    return db_client

def main():
    db_client = create_DB_connection()
    repository = Repository(db_client)

    try:
        # URLをデータベースから取得
        data = repository.get_urls()
        print(data)


        for datum in data:
            url = datum['ec_url']
            scraper = ScraperContext(get_scraper(url))
            product_info = scraper.scrape(url)
            repository.fill_db(product_info)
            
    finally:
        db_client.close()

if __name__ == "__main__":
    url = 'https://www.amazon.com/ELEMENT-Element14-Raspberry-Pi-Motherboard/dp/B07P4LSDYV'
    api_key = os.getenv('PhantomJsCloud_API_KEY')
    client = PhantomJSCloudClient(api_key)
    scraper = AmazonScraper()
    scraper.get_price(scraper.scrape(url))

#    main = Main(scraper, url, client)
#    main.run()


'''
<div id="rightCol" class="rightCol">
<div id="apex_offerDisplay_desktop" class="celwidget"
<span class="a-offscreen">

'''