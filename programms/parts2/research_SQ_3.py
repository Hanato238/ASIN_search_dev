import os
import dotenv
import time

# for DatabaseClient
import mysql.connector

# for KeepaClient
import keepa

# for SpAPIClitne
from sp_api.api import CatalogItems
from sp_api.base.exceptions import SellingApiRequestThrottledException

# for ImageSearcher
from google.cloud import vision


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

# !! これは3カ月間販売数しか取得していない！
class KeepaClient:
    def __init__(self, api_key):
        self.api = keepa.Keepa(api_key)

    def get_sales_rank_drops(self, asin):
        products = self.api.query(asin, domain='JP', stats=90)
        return products[0]['stats']['salesRankDrops90']


class AmazonAPIClient:
    def __init__(self, refresh_token, lwa_app_id, lwa_client_secret, marketplace):
        self.credentials = {
            'refresh_token': refresh_token,
            'lwa_app_id': lwa_app_id,
            'lwa_client_secret': lwa_client_secret
        }
        self.marketplace = marketplace

    def fetch_product_details(self, asin):
        try:
            details = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token']).get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            return details.payload
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.fetch_product_details(asin)

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


class Repository:
    def __init__(self, db_client):
        self.db_client = db_client
    
    def get_products(self):
        query = "SELECT id, asin, image_url FROM products_master WHERE weight IS NULL"
        return self.db_client.execute_query(query)
  
    def get_positive_list(self):
        query = "SELECT ec_site FROM ec_sites WHERE to_research = TRUE"
        return [item['ec_site'] for item in self.db_client.execute_query(query)]


    def update_product(self, product_id, weight, weight_unit, image_url):
        query = """
            UPDATE products_master
            SET weight = %s,
            weight_unit = %s,
            image_url = %s,
            last_search = NOW()
            WHERE id = %s;
        """
        params = (weight, weight_unit, image_url, product_id)
        return self.db_client.execute_update(query, params)

    def update_ec_url(self, product_id, ec_url):
        query = "SELECT * FROM products_ec WHERE asin_id = %s AND ec_url = %s"
        if not self.db_client.execute_query(query, (product_id, ec_url)):
            insert_query = "INSERT INTO products_ec (asin_id, ec_url) VALUES (%s, %s)"
            self.db_client.execute_update(insert_query, (product_id, ec_url))
        else:
            print("URL already exists in the database")

    def update_product_status(self, product_id):
        update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
        self.db_client.execute_update(update_query, (product_id,))

    def update_sales_rank(self, asin, sales_rank_drops):
        insert_query = """
            UPDATE products_detail pd
            JOIN products_master pm ON pd.asin_id = pm.id
            SET pd.three_month_sales = %s
            WHERE pm.asin = %s;
        """
        print(asin, sales_rank_drops)
        self.db_client.execute_update(insert_query, (sales_rank_drops, asin))


class SalesRankUpdater:
    def __init__(self, db_client, keepa_client):
        self.db_client = db_client
        self.keepa_client = keepa_client

    def get_sales_rank(self, asin):
        sales_rank_drops = self.keepa_client.get_sales_rank_drops(asin)
        result = {'asin':asin, 'sales_rank_drops':sales_rank_drops}
        return result

    def update_sales_rank(self, asin, sales_rank_drops):
        self.db_client.update_sales_rank(asin, sales_rank_drops)


class AmazonProductUpdater:
    def __init__(self, db_client, api_client):
        self.db_client = db_client
        self.api = api_client

    def fetch_product_details(self, product):
        product_id, asin = product['id'], product['asin']
        details = self.api.fetch_product_details(asin)

        weight = details['attributes'].get('item_package_weight', [{'value': -1}])[0]['value']
        if weight == 0 or weight == -1:
            weight = details['attributes'].get('item_weight', [{'value': -1}])[0]['value']

        weight_unit = details['attributes'].get('item_package_weight', [{'unit': ''}])[0]['unit']
        if not weight_unit:
            weight_unit = details['attributes'].get('item_weight', [{'unit': ''}])[0]['unit']

        images = details['images'][0]['images']
        if images == []:
            image_url = ''
            print(f'No image_url found for ASIN {asin}')
        else:
            image_url = images[0]['link']

        print(f'ASIN {asin} weights {weight}{weight_unit}')
        details = {'id':product_id, 'asin':asin, 'weight':weight, 'weight_unit':weight_unit, 'image_url':image_url}
        return details
    
    def product_details_updater(self, product_details):
        self.db_client.update_product(
            product_details['id'],
            product_details['weight'],
            product_details['weight_unit'],
            product_details['image_url']
        )
        

class ImageSearchService:
    def __init__(self, repository_search_image, searcher):
        self.repository_search_image = repository_search_image
        self.searcher = searcher
    
    def process_product(self, product, positive_list):
        product_id = product['id']
        image_url = product['image_url']
        print(f'Processing product_id: {product_id}, image_url: {image_url}')

        ec_urls = self.searcher.search_image(image_url, positive_list)
        print(f'Found ec_url: {ec_urls}')

        if ec_urls == None:
            self.repository_search_image.update_ec_url(product_id, -1)
            print("No matching URL found")
        else:
            for ec_url in ec_urls:
                self.repository_search_image.update_ec_url(product_id, ec_url)

        self.repository_search_image.update_product_status(product_id) 


def main():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    repository = Repository(db_client)

    api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = KeepaClient(api_key)
    sales_rank_updater = SalesRankUpdater(repository, keepa_client)

    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    api_client = AmazonAPIClient(**sp_credentials)
    details_updater = AmazonProductUpdater(repository, api_client)

    searcher = ImageSearcher()
    service = ImageSearchService(repository, searcher)
    positive_list = repository.get_positive_list()
    print(f"Positive list: {positive_list}")

    products = repository.get_products()
    if not products:
        print("No products to process")

    # product = {'id', 'asin', 'image_url'}
    # details = {'id', 'asin', 'weight', 'weight_unit', 'image_url'}
    # sales_rank_drops = {'asin', 'sales_rank_drops'}
    for product in products:
        details = details_updater.fetch_product_details(product)
        details_updater.product_details_updater(details)
        sales_rank_drops = sales_rank_updater.get_sales_rank(details['asin'])
        sales_rank_updater.update_sales_rank(sales_rank_drops['asin'], sales_rank_drops['sales_rank_drops'])
        if sales_rank_drops['sales_rank_drops'] == 0 or sales_rank_drops['sales_rank_drops'] > 200:
            repository.update_product_status(details['id'])
        else:
            service.process_product(details, positive_list)

        # calculatorが必要 あとはpriceだけ・・・
        # all_details = calc.get_all_details(details['asin'])
        # calc.calc_all_details(all_details)  


    db_client.close()

if __name__ == "__main__":
    main()
