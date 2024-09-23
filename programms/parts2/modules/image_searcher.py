from google.cloud import vision
import dotenv
import re

dotenv.load_dotenv()


class ImageSearcher:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        # positive list + negative list方式にする? : positive list方式 + salvage方式にする
    
    def search_image(self, image_url, positive_list=None):
        print(image_url)
        if image_url == None:
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

        return ec_urls if ec_urls else None
    


class RepositoryToGet:
    def __init__(self, db_client):
        self.db = db_client

    def get_positive_list(self):
        query = "SELECT ec_site FROM ec_sites WHERE to_research = TRUE"
        return [item['ec_site'] for item in self.db.execute_query(query)]

    def get_products_to_process(self):
        query = "SELECT * FROM products_master WHERE ec_search IS NULL AND image_url IS NOT NULL"
        return self.db.execute_query(query)
    
    # 統合の際にget_products_to_processと置換
    def get_product_to_process(self, record):
        query = "SELECT * FROM products_master WHERE asin = %s"
        return self.db.execute_query(query, (record['asin'], ))
    

class RepositoryToUpdate:
    def __init__(self, db_client):
        self.db_client = db_client

    def update_ec_url(self, record):
        asin_id = record['asin_id']
        ec_url = record['ec_url']
        query = "SELECT * FROM products_ec WHERE asin_id = %s AND ec_url = %s"
        if not self.db.execute_query(query, (asin_id, ec_url)):
            insert_query = "INSERT INTO products_ec (asin_id, ec_url) VALUES (%s, %s)"
            self.db.execute_update(insert_query, (asin_id, ec_url))
        else:
            print("URL already exists in the database")

    def update_product_status(self, record):
        update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
        self.db.execute_update(update_query, (record['id'],))
    

class ImageSearchService:
    def __init__(self, database_client):
        self.searcher = ImageSearcher()
        self.get = RepositoryToGet(database_client)
        self.update = RepositoryToUpdate(database_client)
    
    def check_urls(self, url):
        patterns = {
            "Amazon": r"https:\\\\/\\\\/www\\\\.amazon\\\\.(com(\\\\.au|\\\\.be|\\\\.br|\\\\.mx|\\\\.cn|\\\\.sg)?|ca|cn|eg|fr|de|in|it|co\\\\.(jp|uk)|nl|pl|sa|sg|es|se|com\\\\.tr|ae)\\\\/(?:dp|gp|[^\\\\/]+\\\\/dp)\\\\/[A-Z0-9]{10}(?:\\\\/[^\\\\/]*)?(?:\\\\?[^ ]*)?",
            "Walmart": r"https:\\\\/\\\\/www\\\\.walmart\\\\.(com|ca)\\\\/ip\\\\/[A-Za-z0-9-]+\\\\/[A-Za-z0-9]+",
            "eBay": r"https:\/\/www\.ebay\.com\/itm\/.*"
        }
        for name, pattern in patterns.items():
            if re.match(pattern, url):
                return True
            else:
                return False
            
    def process_image_url(self, record):
        positive_list = self.get.get_positive_list()
        ec_urls = self.searcher.search_image(record['image_url'], positive_list)
        record_product_ec = {'id': '', 'asin_id': record['id'], 'price':'', 'price_unit':'', 'availability':'', 'ec_url':''}
        for ec_url in ec_urls:
            if self.check_urls(ec_url):
                record_product_ec['ec_url'] = ec_url
                self.update.update_ec_url(record_product_ec)
            else:
                print("No matching URL found")
            self.update.update_product_status(record) 

def image_searcher(database_client):
    return ImageSearchService(database_client)