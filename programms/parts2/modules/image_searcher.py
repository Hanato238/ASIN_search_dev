from google.cloud import vision
import dotenv
import re
import logging
from typing import List, Optional, Dict, Any

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class ImageSearcher:
    def __init__(self) -> None:
        self.client = vision.ImageAnnotatorClient()
        # positive list + negative list方式にする? : positive list方式 + salvage方式にする
    
    def search_image(self, image_url: str, positive_list: Optional[List[str]] = None) -> Optional[List[str]]:
        logging.info(f"Searching image from {image_url}")
        if image_url == None:
            logging.info("No image URL found")
            return None
        image = vision.Image()

        image.source.image_uri = image_url

        response = self.client.web_detection(image=image)
        annotations = response.web_detection
        ec_urls = []

        if annotations.pages_with_matching_images:
            for page in annotations.pages_with_matching_images:
                    if any(domain in page.url for domain in positive_list):
                        ec_urls.append(page.url)

        logging.info(f"Found {len(ec_urls)} matching URLs")
        return ec_urls if ec_urls else None
    


class RepositoryToGet:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def get_positive_list(self) -> List[str]:
        query = "SELECT ec_site FROM ec_sites WHERE to_research = TRUE"
        result = [item['ec_site'] for item in self.db_client.execute_query(query)]
        logging.info(f"Positive list: {result}")
        return result
    
    def get_products_to_process(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_master WHERE ec_search IS NULL OR ec_search = FALSE" 
        result = self.db_client.execute_query(query)
        logging.info(f"Found {len(result)} products to process")
        return result
    
    def get_image_url_from_asin_id(self, asin_id: int) -> Optional[str]:
        query = "SELECT image_url FROM products_master WHERE id = %s"
        result = self.db_client.execute_query(query, (asin_id, ))
        image_url = result[0]['image_url'] if result else None
        logging.info(f"Image URL for asin_id {asin_id}: {image_url}")
        return image_url
    

class RepositoryToUpdate:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def update_ec_url(self, record: Dict[str, Any]) -> None:
        asin_id = record['asin_id']
        ec_url = record['ec_url']
        query = "SELECT * FROM products_ec WHERE asin_id = %s AND ec_url = %s"
        if not self.db_client.execute_query(query, (asin_id, ec_url)):
            insert_query = "INSERT INTO products_ec (asin_id, ec_url) VALUES (%s, %s)"
            self.db_client.execute_update(insert_query, (asin_id, ec_url))
            logging.info(f"Inserted new EC URL: {ec_url} for asin_id {asin_id}")
        else:
            logging.info("URL already exists in the database")

    def update_salvage_ec(self, record: Dict[str, Any]) -> None:
        query = "INSERT salvage_ec (asin_id, ec_url_not_supported) VALUES (%s, %s)"
        self.db_client.execute_update(query, (record['asin_id'], record['ec_url']))

    def update_product_status(self, record: Dict[str, Any]) -> None:
        update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
        #update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
        self.db_client.execute_update(update_query, (record['id'],))
        logging.info(f"Updated product status for asin_id {record['id']}")
    

class ImageSearchService:
    def __init__(self, database_client: Any) -> None:
        self.searcher = ImageSearcher()
        self.get = RepositoryToGet(database_client)
        self.update = RepositoryToUpdate(database_client)

    def get_products_to_process(self) -> List[Dict[str, Any]]:
        return self.get.get_products_to_process()
                
    def process_image_url(self, record: Dict[str, Any]) -> None:
        self.update.update_product_status(record)
        positive_list = self.get.get_positive_list()
        image_url = self.get.get_image_url_from_asin_id(record['id'])
        ec_urls = self.searcher.search_image(image_url, positive_list)
        if ec_urls is None:
            logging.info("No matching URL found")
            return
        record_product_ec = {'id': '', 'asin_id': record['id'], 'price':'', 'price_unit':'', 'availability':'', 'ec_url':'', 'is_filled': ''}
        for ec_url in ec_urls:
            record_product_ec['ec_url'] = ec_url
            self.update.update_ec_url(record_product_ec)

"""
# 正規表現が厳密にわかれば使用
            try:
                if self.check_urls(ec_url):
                    self.update.update_ec_url(record_product_ec)
                else:
                    self.update.update_salvage_ec(record_product_ec)
                    logging.info("URL not supported")
            except Exception as e:
                logging.info("An error occurred: {e}")
                continue
"""

def image_searcher(database_client: Any) -> ImageSearchService:
    return ImageSearchService(database_client)