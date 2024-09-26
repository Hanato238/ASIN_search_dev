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
        query = "SELECT * FROM products_master WHERE ec_search IS NULL AND image_url IS NOT NULL"
        result = self.db_client.execute_query(query)
        logging.info(f"Found {len(result)} products to process")
        return result
    
    def get_image_url_from_asin_id(self, asin_id: int) -> Optional[str]:
        query = "SELECT image_url FROM products_master WHERE id = %s"
        result = self.db_client.execute_query(query, (asin_id, ))
        image_url = result[0]['image_url'] if result else None
        logging.info(f"Image URL for asin_id {asin_id}: {image_url}")
        return image_url
    
    # 統合の際にget_products_to_processと置換
    def get_product_to_process(self, record):
        query = "SELECT * FROM products_master WHERE asin = %s"
        return self.db_client.execute_query(query, (record['asin'], ))
    

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

    def update_product_status(self, record: Dict[str, Any]) -> None:
        update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
        self.db_client.execute_update(update_query, (record['id'],))
        logging.info(f"Updated product status for asin_id {record['asin_id']}")
    

class ImageSearchService:
    def __init__(self, database_client: Any) -> None:
        self.searcher = ImageSearcher()
        self.get = RepositoryToGet(database_client)
        self.update = RepositoryToUpdate(database_client)
    
    def check_urls(self, url: str) -> bool:
        patterns = {
            "Amazon": r"https:\\\\/\\\\/www\\\\.amazon\\\\.(com(\\\\.au|\\\\.be|\\\\.br|\\\\.mx|\\\\.cn|\\\\.sg)?|ca|cn|eg|fr|de|in|it|co\\\\.(jp|uk)|nl|pl|sa|sg|es|se|com\\\\.tr|ae)\\\\/(?:dp|gp|[^\\\\/]+\\\\/dp)\\\\/[A-Z0-9]{10}(?:\\\\/[^\\\\/]*)?(?:\\\\?[^ ]*)?",
            "Walmart": r"https:\\\\/\\\\/www\\\\.walmart\\\\.(com|ca)\\\\/ip\\\\/[A-Za-z0-9-]+\\\\/[A-Za-z0-9]+",
            "eBay": r"https:\/\/www\.ebay\.com\/itm\/.*"
        }
        for name, pattern in patterns.items():
            if re.match(pattern, url):
                logging.info(f"Found matching URL: {name}: {url}")
                return True
            return False
            
    def process_image_url(self, record: Dict[str, Any]) -> None:
        positive_list = self.get.get_positive_list()
        image_url = self.get.get_image_url_from_asin_id(record['asin_id'])
        ec_urls = self.searcher.search_image(image_url, positive_list)
        record_product_ec = {'id': '', 'asin_id': record['asin_id'], 'price':'', 'price_unit':'', 'availability':'', 'ec_url':''}
        for ec_url in ec_urls:
            if self.check_urls(ec_url):
                record_product_ec['ec_url'] = ec_url
                self.update.update_ec_url(record_product_ec)
            else:
                logging.info("No matching URL found")
            self.update.update_product_status(record) 

def image_searcher(database_client: Any) -> ImageSearchService:
    return ImageSearchService(database_client)