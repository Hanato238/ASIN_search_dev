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
    
class ImageSearchService:
    def __init__(self, repository_search_image, searcher):
        self.repository_search_image = repository_search_image
        self.searcher = searcher
    
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
            
    def process_product(self, product):
        product_id = product['id']
        image_url = product['image_url']
        print(f'Processing product_id: {product_id}, image_url: {image_url}')

        positive_list = self.repository_search_image.get_positive_list()
        ec_urls = self.searcher.search_image(image_url, positive_list)
        print(f'Found ec_url: {ec_urls}')
        
        for ec_url in ec_urls:
            if self.check_urls(ec_url):
                self.repository_search_image.save_ec_url(product_id, ec_url)
            else:
                print("No matching URL found")
            self.repository_search_image.update_product_status(product_id) 

def image_searcher():
    return ImageSearcher()

def image_search_service(repository_search_image, searcher=ImageSearcher()):
    return ImageSearchService(repository_search_image, searcher)

class RepositoryToSearchImage:
    def __init__(self, db_client):
        self.db = db_client

    def get_positive_list(self):
        query = "SELECT ec_site FROM ec_sites WHERE to_research = TRUE"
        return [item['ec_site'] for item in self.db.execute_query(query)]

    def get_products_to_process(self):
        query = "SELECT id, image_url FROM products_master WHERE ec_search IS NULL AND image_url IS NOT NULL"
        return self.db.execute_query(query)
    
    # 統合の際にget_products_to_processと置換
    def get_product_to_process(self, asin):
        query = "SELECT image_url FROM products_master WHERE asin = %s"
        return self.db.execute_query(query, (asin, ))

    def save_ec_url(self, product_id, ec_url):
        query = "SELECT * FROM products_ec WHERE asin_id = %s AND ec_url = %s"
        if not self.db.execute_query(query, (product_id, ec_url)):
            insert_query = "INSERT INTO products_ec (asin_id, ec_url) VALUES (%s, %s)"
            self.db.execute_update(insert_query, (product_id, ec_url))
        else:
            print("URL already exists in the database")

    def update_product_status(self, product_id):
        update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
        self.db.execute_update(update_query, (product_id,))

def repository_to_search_image(db_client):
    return RepositoryToSearchImage(db_client)