import os
import dotenv

# for scraper
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests
from time import sleep

# for DB
import mysql.connector
import pymysql
from google.cloud.sql.connector import Connector

dotenv.load_dotenv()


class DatabaseClient:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor(dictionary=True)
        print("connected to DB")

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

class Repository:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_urls(self):
        query = 'SELECT id, ec_url FROM products_ec WHERE price IS NULL AND ec_url != -1;'
        return self.db_client.execute_query(query)
    
    def fill_db(self, price, id):
        query="""
            UPDATE products_ec 
            SET price = %s
            WHERE id = %s;
         """
        self.db_client.execute_update(query, (price, id))

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

class BrightDataAPI:
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.api_key = os.getenv('BRIGHTDATA_API_KEY')

    def get_snapshot_id(self, url, dataset_name):
        dataset_id = self.dataset_id
        if not dataset_id:
            raise ValueError(f"Dataset name '{dataset_name}' not found in dataset dictionary.")
        
        api_url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "url": url
        }
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        snapshot_id = response.json()['snapshot_id']
        print(snapshot_id)
        return snapshot_id

    def get_price(self, snapshot_id, max_retries=3):
        url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                print(data)
                if isinstance(data, dict) and data.get('status') == 'running':
                    raise ValueError("Snapshot is still running.")
                elif isinstance(data, list) and 'final_price' in data[0]:
                    return data[0]['final_price']
            except (requests.exceptions.RequestException, ValueError) as e:
                retries += 1
                if retries >= max_retries:
                    return -1
                sleep(15 * retries)  # Exponential backoff

class ScraperFactory:
    @staticmethod
    def create_scraper(scraper_type, dataset_id):
        if scraper_type == 'amazon':
            return AmazonScraper(dataset_id)
        elif scraper_type == 'walmart':
            return WalmartScraper(dataset_id)
        elif scraper_type == 'ebay':
            return EBayScraper(dataset_id)
        else:
            raise ValueError(f"Scraper type '{scraper_type}' is not supported.")

class AmazonScraper(BrightDataAPI):
    def __init__(self, dataset_id):
        super().__init__(dataset_id)

class WalmartScraper(BrightDataAPI):
    def __init__(self, dataset_id):
        super().__init__(dataset_id)

class EBayScraper(BrightDataAPI):
    def __init__(self, dataset_id):
        super().__init__(dataset_id)


def scraper(url):
    if 'amazon' in url:
        dataset_id = 'gd_l7q7dkf244hwjntr0'
        ec_site = 'amazon'
    elif 'walmart' in url:
        dataset_id = 'gd_l95fol7l1ru6rlo116'
        ec_site = 'walmart'
    elif 'ebay' in url:
        dataset_id = 'gd_ltr9mjt81n0zzdk1fb'
        ec_site = 'ebay'
    
    scraper_factory = ScraperFactory()
    print(ec_site)
    scraper = scraper_factory.create_scraper(ec_site, dataset_id)
    snapshot_id = scraper.get_snapshot_id(url, ec_site)
    price = scraper.get_price(snapshot_id)
    return price

def main():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    repository = Repository(db_client)
    urls = repository.get_urls()
    for url in urls:
        price = scraper(url['ec_url'])
        repository.fill_db(price, url['id'])

if __name__ == "__main__":
    main()