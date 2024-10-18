import requests
import re
from time import sleep
from typing import Dict, List, Union, Any
from programms.parts3.domain.interface.i_api_client import IScraper
from programms.parts3.infrastructure.object.dto import EcData
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BrightDataAPI:
    _DATASET_DICT = {
        'walmart': 'gd_l95fol7l1ru6rlo116',
        'amazon': 'gd_l7q7dkf244hwjntr0',
        'ebay': 'gd_ltr9mjt81n0zzdk1fb'
    }

    def __init__(self, dataset_id, api_key) -> None:
        self.dataset_id = dataset_id
        self.api_key = api_key

    # dataは未処理：ECサイトごとに構造が異なるから
    def run(self, url:str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        snapshot_id = self.get_snapshot_id(url)
        data = self.get_detail(snapshot_id)
        return data
        
    def get_snapshot_id(self, url: str) -> str:
        dataset_id = self.dataset_id
       
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

# dataは最終的にはどのように加工すべきか。値オブジェクトorDTO？
class AmazonScraper(IScraper):
    def __init__(self, bright_data_api: BrightDataAPI) -> None:
        self.bright_data_api = bright_data_api

    def scrape(self, url:str) -> EcData:
        data = self.bright_data_api.run(url)
        price = data[0]['final_price']
        currency = data[0]['currency']
        availability = data[0]['availability']
        return data
        
class WalmartScraper(IScraper):
    def __init__(self, bright_data_api: BrightDataAPI) -> None:
        self.bright_data_api = bright_data_api

    def scrape(self, url:str) -> EcData:
        data = self.bright_data_api.run(url)
        price = data[0]['final_price']
        currency = data[0]['currency']
        availability = data[0]['available_for_delivery']
        return data
    
class EbayScraper(IScraper):
    def __init__(self, bright_data_api: BrightDataAPI) -> None:
        self.bright_data_api = bright_data_api

    def scrape(self, url:str) -> EcData:
        data = self.bright_data_api.run(url)
        price = re.findall(r'[\d.]+', data[0]['price'])[0]
        currency = data[0]['currency']
        return data