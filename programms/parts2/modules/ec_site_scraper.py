import requests
import dotenv
import os
import requests
from time import sleep
import logging
from typing import Dict, List, Union, Any, str

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

dataset_dict = {
    'walmart': 'gd_l95fol7l1ru6rlo116',
    'amazon': 'gd_l7q7dkf244hwjntr0',
    'ebay': 'gd_ltr9mjt81n0zzdk1fb'
}

class BrightDataAPI:
    def __init__(self, dataset_id) -> None:
        self.dataset_id = dataset_id
        self.api_key = os.getenv('BRIGHTDATA_API_KEY')

    def get_snapshot_id(self, url: str, dataset_name: str) -> str:
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
        logging.info(f"Snapshot ID: {snapshot_id}")
        return snapshot_id

    def get_detail(self, snapshot_id: str, max_retries: int=5) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
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
                logging.warning(f"Failed to get data from BrightData API. Retrying... ({retries}/{max_retries})")
                if retries >= max_retries:
                    raise e
                sleep(10 * retries)

class ScraperFactory:
    @staticmethod
    def create_scraper(scraper_type: str, dataset_id: str) -> BrightDataAPI:
        if scraper_type == 'amazon':
            return AmazonScraper(dataset_id)
        elif scraper_type == 'walmart':
            return WalmartScraper(dataset_id)
        elif scraper_type == 'ebay':
            return EBayScraper(dataset_id)
        else:
            raise ValueError(f"Scraper type '{scraper_type}' is not supported.")

class AmazonScraper(BrightDataAPI):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id)

    def get_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['final_price']
        data_scraped['currency'] = data[0]['currency']
        data_scraped['availability'] = data[0]['is_available']
        return data_scraped

class WalmartScraper(BrightDataAPI):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id)

    def get_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['final_price']
        data_scraped['currency'] = data[0]['currency']
        data_scraped['availability'] = data[0]['available_for_delivery']
        return data_scraped

class EBayScraper(BrightDataAPI):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id)
    
    def get_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['price']
        data_scraped['currency'] = data[0]['currency']
        #data_scraped['availability'] = data[0]['is_available']
        return data_scraped

class Repository:
    def __init__(self, database_client: Any) -> None:
        self.database_client = database_client
    
    def get_ec_urls(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        asin_id = record['id']
        query = f"SELECT * FROM products_ec WHERE asin_id = {asin_id}"
        return self.database_client.execute_query(query)
    
    def update_ec_url(self, asin_id: int, data: Dict[str, Any]) -> None:
        price = data['price']
        price_unit = data['currency']
        availability = data['availability']
        query = f"INSERT INTO products_ec (asin_id, price, price_unit, availability, ec_url) VALUES ({asin_id}, {price}, '{price_unit}', {availability}, '{data['ec_url']}')"
        self.database_client.execute_query(query)

class ScraperFacade:
    def __init__(self, database_client: Any) -> None:
        self.repository = Repository(database_client)

    def scrape_and_save(self, record: Dict[str, Any]) -> None:
        asin_id = record['asin_id']
        url = record['ec_url']
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
        self.repository.update_ec_url(asin_id, data_scraped)


def get_scraper(database_client: Any) -> ScraperFacade:
    return ScraperFacade(database_client)