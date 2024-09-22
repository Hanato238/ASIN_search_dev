import requests
import dotenv
import os
import requests
from time import sleep

dotenv.load_dotenv()

dataset_dict = {
    'walmart': 'gd_l95fol7l1ru6rlo116',
    'amazon': 'gd_l7q7dkf244hwjntr0',
    'ebay': 'gd_ltr9mjt81n0zzdk1fb'
}

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

    def get_detail(self, snapshot_id, max_retries=5):
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
                if isinstance(data, dict) and data.get('status') == 'running':
                    raise ValueError("Snapshot is still running.")
                elif isinstance(data, list):
                    return data
            except (requests.exceptions.RequestException, ValueError) as e:
                retries += 1
                if retries >= max_retries:
                    raise e
                sleep(10 * retries)  # Exponential backoff

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

    def get_data(self, data):
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['final_price']
        data_scraped['currency'] = data[0]['currency']
        data_scraped['availability'] = data[0]['is_available']
        return data_scraped

class WalmartScraper(BrightDataAPI):
    def __init__(self, dataset_id):
        super().__init__(dataset_id)

    def get_data(self, data):
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['final_price']
        data_scraped['currency'] = data[0]['currency']
        data_scraped['availability'] = data[0]['available_for_delivery']
        return data_scraped

class EBayScraper(BrightDataAPI):
    def __init__(self, dataset_id):
        super().__init__(dataset_id)
    
    def get_data(self, data):
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['price']
        data_scraped['currency'] = data[0]['currency']
        #data_scraped['availability'] = data[0]['is_available']
        return data_scraped

class Repository:
    def __init__(self, database_client):
        self.database_client = database_client
    
    def get_ec_urls(self, asin_id):
        query = f"SELECT ec_url FROM products_ec WHERE asin_id = {asin_id}"
        return self.database_client.execute_query(query)
    
    def save_ec_url(self, asin_id, data):
        price = data['price']
        price_unit = data['currency']
        availability = data['availability']
        query = f"INSERT INTO products_ec (asin_id, price, price_unit, availability, ec_url) VALUES ({asin_id}, {price}, '{price_unit}', {availability}, '{data['ec_url']}')"
        self.database_client.execute_query(query)

class ScraperFacade:
    def __init__(self, database_client):
        self.repository = Repository(database_client)

    def scrape_and_save(self, asin_id, url):
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
        scraper = scraper_factory.create_scraper(ec_site, dataset_id)
        snapshot_id = scraper.get_snapshot_id(url, ec_site)
        data = scraper.get_detail(snapshot_id)
        data_scraped = scraper.get_data(data)
        data_scraped['ec_url'] = url
        self.repository.save_ec_url(asin_id, data_scraped)


def get_scraper():
    return ScraperFacade()