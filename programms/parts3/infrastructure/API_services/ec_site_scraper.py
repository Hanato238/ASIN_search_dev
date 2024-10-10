import requests
import dotenv
import os
import requests
from time import sleep
import re
import logging
from typing import Dict, List, Union, Any, Tuple

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
            except ValueError as e:
                retries += 1
                logging.info(f"Failed to get data from BrightData API. Retrying... ({retries}/{max_retries})")
                if retries >= max_retries:
                    raise e
                sleep(10 * retries)
            except requests.exceptions.RequestException as e:
                logging.error(f"Error getting data from BrightData API: {e}")
                raise e

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
w
class AmazonScraper(BrightDataAPI):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id)
        self.pattern = re.compile(r"https:\\\\/\\\\/www\\\\.amazon\\\\.(com(\\\\.au|\\\\.be|\\\\.br|\\\\.mx|\\\\.cn|\\\\.sg)?|ca|cn|eg|fr|de|in|it|co\\\\.(jp|uk)|nl|pl|sa|sg|es|se|com\\\\.tr|ae)\\\\/(?:dp|gp|[^\\\\/]+\\\\/dp)\\\\/[A-Z0-9]{10}(?:\\\\/[^\\\\/]*)?(?:\\\\?[^ ]*)?")

    def scrape_data(self, scraper: Any, url: str) -> Dict[str, Any]:
        if self.pattern.match(url) is None:
            raise ValueError("URL dose not match the pattern")
        snapshot_id = scraper.get_snapshot_id(url, 'amazon')
        data = scraper.get_detail(snapshot_id)
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['final_price']
        data_scraped['currency'] = data[0]['currency']
        data_scraped['availability'] = data[0]['is_available']
        return data_scraped

class WalmartScraper(BrightDataAPI):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id)
        self.pattern = re.compile(r"https:\\\\/\\\\/www\\\\.walmart\\\\.(com|ca)\\\\/ip\\\\/[A-Za-z0-9-]+\\\\/[A-Za-z0-9]+")

    def scrape_data(self, scraper: Any, url: str) -> Dict[str, Any]:
        if not self.pattern.match(url):
            raise ValueError("URL dose not match the pattern")
        snapshot_id = scraper.get_snapshot_id(url, 'walmart')
        data = scraper.get_detail(snapshot_id)
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = data[0]['final_price']
        data_scraped['currency'] = data[0]['currency']
        data_scraped['availability'] = data[0]['available_for_delivery']
        return data_scraped

class EBayScraper(BrightDataAPI):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id)
        self.pattern = re.compile(r"https:\/\/www\.ebay\.com\/itm\/.*")

    def scrape_data(self, scraper: Any, url: str) -> Dict[str, Any]:
        if not self.pattern.match(url):
            raise ValueError("URL dose not match the pattern")
        snapshot_id = scraper.get_snapshot_id(url, 'ebay')
        data = scraper.get_detail(snapshot_id)
        data_scraped = {'price':'', 'currency':'', 'condition':'', 'availability':''}
        data_scraped['price'] = re.findall(r'[\d.]+', data[0]['price'])[0]
        data_scraped['currency'] = data[0]['currency']
        #data_scraped['availability'] = data[0]['is_available']
        return data_scraped

class RepositoryToGet:
    def __init__(self, database_client: Any) -> None:
        self.database_client = database_client
    
    # record_products_detail -> records_products_ec
    def get_ec_urls_to_process(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        asin_id = record['asin_id']
        query = f"SELECT * FROM products_ec WHERE asin_id = {asin_id}"
        return self.database_client.execute_query(query)

    # None -> records_products_ec
    def get_products_to_process(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_ec WHERE is_filled IS NULL or is_filled = FALSE"
        return self.database_client.execute_query(query)
    
class RepositoryToUpdate:
    def __init__(self, database_client: Any) -> None:
        self.database_client = database_client

    # record_products_ec + scraped_date -> None : update record_products_ec
    def update_ec_url(self, record: Dict[str, Any]) -> None:
        price = record['price']
        price_unit = record['price_unit']
        availability = record['availability']
        query = """
            UPDATE products_ec 
            SET price = %s, 
            price_unit = %s, 
            availability = %s
            WHERE id = %s;
        """
        #query = f"INSERT INTO products_ec (asin_id, price, price_unit, availability, ec_url) VALUES ({asin_id}, {price}, '{price_unit}', {availability}, '{data['ec_url']}')"
        self.database_client.execute_update(query, (price, price_unit, availability, record['id']))
        logging.info(f"Update ASIN_id: {record['asin_id']} with Scraped data: {price, price_unit, availability}")  

    # record_products_ec -> None: make is_filled = True
    def update_products_ec_status(self, record: Dict[str, Any]) -> None:
        query = "UPDATE products_ec SET is_filled = True WHERE id = %s"
        self.database_client.execute_update(query, (record['id'],))

    def update_supportive(self, record: Dict[str, Any], is_supported: bool=False) -> None:
        query = "UPDATE products_ec SET is_supported = %s WHERE id = %s"
        self.database_client.execute_update(query, (is_supported, record['id']))

    def update_is_filled(self, record: Dict[str, Any], is_filled: bool=True) -> None:
        query = "UPDATE products_ec SET is_filled = %s WHERE id = %s"
        self.database_client.execute_update(query, (is_filled, record['id']))

class ScraperFacade:
    def __init__(self, database_client: Any) -> None:
        self.get = RepositoryToGet(database_client)
        self.update = RepositoryToUpdate(database_client)

    def get_products_to_process(self) -> List[Dict[str, Any]]:
        return self.get.get_products_to_process()

    # record_products_ec -> None : scrape and fill
    def process_scrape(self, record: Dict[str, Any]) -> None:
        self.update.update_products_ec_status(record)
        url = record['ec_url']
        try:
            ec_site, dataset_id = self.get_ec_site_and_dataset_id(url)
            scraper = self.create_scraper(ec_site, dataset_id)
            logging.info(f'Scraping data from {url} by {ec_site} scraper')
            data_scraped = scraper.scrape_data(scraper, url)

            self.update_record_with_scraped_data(record, data_scraped)
            self.update.update_supportive(record, True)
        except ValueError as ve:
            logging.info(f"Error: {ve}")
            self.update.update_supportive(record, False)
            self.update.update_is_filled(record, True)
        except Exception as e:
            logging.info(f"Error processing image url: {e}")
            self.update.update_supportive(record, False)
            self.update.update_is_filled(record, True)

    def get_ec_site_and_dataset_id(self, url: str) -> Tuple[str, str]:
        if 'amazon' in url:
            return 'amazon', 'gd_l7q7dkf244hwjntr0'
        elif 'walmart' in url:
            return 'walmart', 'gd_l95fol7l1ru6rlo1s16'
        elif 'ebay' in url:
            return 'ebay', 'gd_ltr9mjt81n0zzdk1fb'
        else:
            raise ValueError(f"EC site not supported: {url}")

    def create_scraper(self, ec_site: str, dataset_id: str) -> Any:
        scraper_factory = ScraperFactory()
        return scraper_factory.create_scraper(ec_site, dataset_id)


#    def scrape_data(self, scraper: Any, url: str, ec_site: str) -> Dict[str, Any]:
#        snapshot_id = scraper.get_snapshot_id(url, ec_site)
#        data = scraper.get_detail(snapshot_id)
#        return scraper.get_data(data)


    def update_record_with_scraped_data(self, record: Dict[str, Any], data_scraped: Dict[str, Any]) -> None:
        record['price'] = data_scraped['price']
        record['price_unit'] = data_scraped['currency']
        record['availability'] = data_scraped['availability']
        if record['price'] is None and record['price_unit'] is None and record['availability'] is None:
            self.update.update_is_filled(record, False)
            raise ValueError("Scraped data is incomplete.")
        else:
            self.update.update_ec_url(record)
            self.update.update_is_filled(record, True)


        
    # record_products_detail -> None : scrape and fill
    #asin_idからスクレイプしたい
    def scrape_and_save(self, record: Dict[str, Any]) -> None:
        ec_urls = self.repository.get_ec_urls_to_process(record)
        for ec_url in ec_urls:
            url = ec_url['ec_url']
            if 'amazon' in url:
                dataset_id = 'gd_l7q7dkf244hwjntr0'
                ec_site = 'amazon'
            elif 'walmart' in url:
                dataset_id = 'gd_l95fol7l1ru6rlo1s16'
                ec_site = 'walmart'
            elif 'ebay' in url:
                dataset_id = 'gd_ltr9mjt81n0zzdk1fb'
                ec_site = 'ebay'
        
            scraper_factory = ScraperFactory()
            scraper = scraper_factory.create_scraper(ec_site, dataset_id)
            snapshot_id = scraper.get_snapshot_id(url)
            data = scraper.get_detail(snapshot_id)
            # ec_urlにfillしたい
            data_scraped = scraper.get_data(data)
            data_scraped['ec_url'] = url
            self.repository.update_ec_url(ec_url, data_scraped)


def get_scraper(database_client: Any) -> ScraperFacade:
    return ScraperFacade(database_client)



# for tester
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
    price = scraper.get_detail(snapshot_id)
    return price