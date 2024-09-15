import mysql.connector
import keepa
import os
import dotenv
import time

from sp_api.api import CatalogItems
from sp_api.base.exceptions import SellingApiRequestThrottledException

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

class KeepaClient:
    def __init__(self, api_key):
        self.api = keepa.Keepa(api_key)
        print("connected to Keepa")

    # 10 tokens per 1 seller (storefront=True:+9 tokens)
    def search_asin_by_seller(self, seller):
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            return products[seller]['asinList']
        except Exception as e:
            print(f"Error fetching ASINs for seller {seller}: {e}")
            return []
    
    # 1.6 - 6.6 tokens per 1 asin (offers=20:+6 tokens per 10 asin)
    def query_seller_info(self, asin):
        return self.api.query(asin, domain='JP', history=False, offers=20, only_live_offers=True)

class AsinSearcher:
    def __init__(self, db_client, keepa_client):
        self.db_client = db_client
        self.keepa_client = keepa_client

    def get_sellers(self):
        sellers = self.db_client.execute_query("SELECT seller FROM sellers")
        return sellers

    def add_product_master(self, asin):
        counts = self.db_client.execute_query("SELECT COUNT(*) FROM products_master WHERE asin = %s", (asin,))
        for count in counts:
            if count['COUNT(*)'] == 0:
                insert_query = """
                    INSERT INTO products_master (asin, last_search, last_sellers_search)
                    VALUES (%s, '2020-01-01', '2020-01-01')
                """
                self.db_client.execute_update(insert_query, (asin,))
                print(f"Added product master for ASIN: {asin}")
        # 追加でproducts_detailにid, asinのみのレコードを追加する

    def get_product_id(self, asin):
        result = self.db_client.execute_query("SELECT id FROM products_master WHERE asin = %s", (asin,))
        return result[0]['id'] if result else None

    def write_asin_to_junction(self, seller, product_id):
        try:
            seller_id = self.db_client.execute_query("SELECT id FROM sellers WHERE seller = %s", (seller,))[0]['id']
            insert_query = """
                INSERT INTO junction (seller_id, product_id, evaluate)
                VALUES (%s, %s, %s)
            """
            self.db_client.execute_update(insert_query, (seller_id, product_id, False))
        except mysql.connector.Error as err:
            print(f"Error: {err}")

# products_detailにid, asinのみのレコードを追加する    
    def add_product_detail(self, asin):
        try:
            insert_query = """
                INSERT INTO products_detail (asin_id)
                VALUE (%s)
            """
            self.db_client.execute_update(insert_query, (self.get_product_id(asin),))
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def process_sellers(self):
        sellers = self.get_sellers()
        for seller in sellers:
            sellerId = seller['seller']
            asins = self.keepa_client.search_asin_by_seller(sellerId)
            print(f'{sellerId} has Asins')
            for asin in asins:
                self.add_product_master(asin)
                self.add_product_detail(asin)
                product_id = self.get_product_id(asin)
                if product_id:
                    self.write_asin_to_junction(sellerId, product_id)

class SellerSearcher:
    def __init__(self, db_client, keepa_client):
        self.db = db_client
        self.api = keepa_client

    def search_seller(self):
        query = "SELECT id, asin FROM products_master"
        products = self.db.execute_query(query)

        for product in products:
            print(f'asin : {product["asin"]}')
            asin = product['asin']
            product_id = product['id']
            seller_info = self.api.query_seller_info(asin)
            extracted_data = self.extract_info(seller_info[0]['offers'])
            print(f'extracted_data : {extracted_data}')

            if not extracted_data:
                print(f"ASIN: {asin} のsellerIDが見つかりませんでした")
                extracted_data = []
                continue
#  競合を追加する処理, ※products_detailのほかの要素はほかのクラスで追加されるがデザインパターン的に大丈夫か？
            num_competitors = self.count_FBA_sellers(extracted_data)
            insert_query = "UPDATE products_detail SET competitors = %s WHERE asin_id = %s AND competitors IS NULL"
            print(f'asin_id:{product_id} num_competitors : {num_competitors}')
            self.db.execute_update(insert_query, (num_competitors, product_id))


            for datum in extracted_data:
                seller = datum["sellerId"]
                count_query = "SELECT COUNT(*) FROM sellers WHERE seller = %s"
                count = self.db.execute_query(count_query, (seller,))[0]['COUNT(*)']

                if count == 0:
                    print(f'add sellerId : {seller}')
                    insert_query = "INSERT INTO sellers (seller, last_search) VALUES (%s, '2020-01-01')"
                    self.db.execute_update(insert_query, (seller,))

                seller_id_query = "SELECT id FROM sellers WHERE seller = %s"
                seller_id = self.db.execute_query(seller_id_query, (seller,))[0]['id']

                junction_query = "INSERT INTO junction (seller_id, product_id, evaluate) VALUES (%s, %s, FALSE)"
                self.db.execute_update(junction_query, (seller_id, product_id))
            print(f"ASIN: {asin} のsellerIDを取得しました: {len(extracted_data)}件")

    def extract_info(self, data):
        result = []
        for item in data:
            if item["isFBA"] and item["condition"] == 1 and item["isShippable"] and item["isPrime"] and item["isScam"] == 0:
                result.append({"sellerId": item["sellerId"], "isAmazon": item["isAmazon"], "isShippable": item["isShippable"], "isPrime": item["isPrime"]})
        return result
    
    def count_FBA_sellers(self,data):
    # Check if any element has isAmazon set to True
        for item in data:
            if item['isAmazon']:
                return 1000
    
        # Count elements where isPrime is True
        prime_count = sum(1 for item in data if item['isPrime'])
        return prime_count

class AmazonProductUpdater:
    def __init__(self, db, refresh_token, lwa_app_id, lwa_client_secret, marketplace):
        self.credentials = {
            'refresh_token': refresh_token,
            'lwa_app_id': lwa_app_id,
            'lwa_client_secret': lwa_client_secret
        }
        self.marketplace =  marketplace
        self.db = db

    def fetch_products(self):
        query = "SELECT id, asin FROM products_master WHERE weight IS NULL"
        return self.db.execute_query(query)

    def fetch_product_details(self, asin):
        try:
            details = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token']).get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            return details.payload
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.fetch_product_details(asin)

    def update_product(self, product_id, weight, weight_unit, image_url):
        query = """
            UPDATE products_master
            SET weight = %s, weight_unit = %s, image_url = %s
            WHERE id = %s
        """
        params = (weight, weight_unit, image_url, product_id)
        self.db.execute_update(query, params)
        print(f"Updated product {product_id}")

    def process_products(self):
        products = self.fetch_products()
        for product in products:
            product_id, asin = product['id'], product['asin']
            details = self.fetch_product_details(asin)

            weight = details['attributes'].get('item_package_weight', [{'value': -1}])[0]['value']
            if weight == 0 or weight == -1:
                weight = details['attributes'].get('item_weight', [{'value': -1}])[0]['value']

            weight_unit = details['attributes'].get('item_package_weight', [{'unit': ''}])[0]['unit']
            if not weight_unit:
                weight_unit = details['attributes'].get('item_weight', [{'unit': ''}])[0]['unit']

            image_url = details['images'][0]['images'][0]['link'] if details['images'] else ''

            self.update_product(product_id, weight, weight_unit, image_url)

class ImageSearcher:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        # positive list + negative list方式にする? : positive list方式 + salvage方式にする
    
    def search_image(self, image_url, positive_list=None):
        image = vision.Image()
        image.source.image_uri = image_url    

        response = self.client.web_detection(image=image)
        annotations = response.web_detection

        if annotations.pages_with_matching_images:
            for page in annotations.pages_with_matching_images:
                if any(domain in page.url for domain in positive_list):
                    print(page.url)
                    return page.url
        return None

class ImageSearchService:
    def __init__(self, db_client):
        self.db = db_client
        self.searcher = ImageSearcher()
    
    # 画像検索を行う対象のECサイトリストを取得
    def get_positive_list(self):
        query = "SELECT ec_site FROM ec_sites WHERE to_research = TRUE"
        positive_list = [item['ec_site'] for item in self.db.execute_query(query)]
        return positive_list
    
    def process_product(self, product, positive_list):
        product_id = product['id']
        image_url = product['image_url']
        print(f'Processing product_id: {product_id}, image_url: {image_url}')

        # 画像検索でURLを取得
        ec_url = self.searcher.search_image(image_url, positive_list)
        print(f'Found ec_url: {ec_url}')
        
        # 得られたec_urlをDBに保存
        if ec_url:
            query = "SELECT * FROM products_ec WHERE asin_id = %s AND ec_url = %s"
            if not self.db.execute_query(query, (product_id, ec_url)):
                insert_query = "INSERT INTO products_ec (asin_id, ec_url) VALUES (%s, %s)"
                self.db.execute_update(insert_query, (product_id, ec_url))
            else:
                print("URL already exists in the database")

            # products_masterテーブルを更新
            update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
            self.db.execute_update(update_query, (product_id,))
        else:
            print("No matching URL found")    

    def run(self):
        targets = self.db.execute_query("SELECT id, image_url FROM products_master WHERE ec_search IS NULL AND image_url IS NOT NULL")
        if len(targets) == 0:
            print("No products to process")
            return
        positive_list = self.get_positive_list()
        for product in targets:
            self.process_product(product, positive_list)


# 以下の関数は、それぞれのクラスのインスタンスを生成し、処理を実行する関数
def get_asins():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    keepa_api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = KeepaClient(keepa_api_key)
    manager = AsinSearcher(db_client, keepa_client)
    try:
        manager.process_sellers()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_client.close()

def get_sellers():
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }
    db_client = DatabaseClient(**db_config)
    keepa_api_key = os.getenv("KEEPA_API_KEY")
    keepa_client = KeepaClient(keepa_api_key)
    searcher = SellerSearcher(db_client, keepa_client)
    searcher.search_seller()
    db_client.close()

def get_details():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    updater = AmazonProductUpdater(db_client, **sp_credentials)
    updater.process_products()
    db_client.close()

def image_search():
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }
    db_client = DatabaseClient(**db_config)
    service = ImageSearchService(db_client)
    service.run()
    db_client.close()

if __name__ == "__main__":
    print("start")
    get_sellers()