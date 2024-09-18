import os
import dotenv
import time

import mysql.connector

import keepa

from sp_api.api import CatalogItems
from sp_api.base.exceptions import SellingApiRequestThrottledException

from google.cloud import vision

dotenv.load_dotenv()

# Clients
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



# Repositories
class RepositoryToGetAsin:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_sellers(self):
        return self.db_client.execute_query("SELECT seller FROM sellers")

    def add_product_master(self, asin):
        counts = self.db_client.execute_query("SELECT COUNT(*) FROM products_master WHERE asin = %s", (asin,))
        if counts[0]['COUNT(*)'] == 0:
            insert_query = """
                INSERT INTO products_master (asin, last_search, last_sellers_search)
                VALUES (%s, '2020-01-01', '2020-01-01')
            """
            self.db_client.execute_update(insert_query, (asin,))
            print(f"Added product master for ASIN: {asin}")

    def get_product_id(self, asin):
        result = self.db_client.execute_query("SELECT id FROM products_master WHERE asin = %s", (asin,))
        return result[0]['id'] if result else None

    def write_asin_to_junction(self, seller, product_id):
        query = "SELECT id FROM sellers WHERE seller = %s"
        seller_id = self.db_client.execute_query(query, (seller,))[0]['id']
        insert_query = """
            INSERT INTO junction (seller_id, product_id, evaluate)
            VALUES (%s, %s, %s)
        """
        self.db_client.execute_update(insert_query, (seller_id, product_id, False))

    def add_product_detail(self, asin_id):
        insert_query = """
            INSERT INTO products_detail (asin_id)
            VALUE (%s)
        """
        self.db_client.execute_update(insert_query, (asin_id,))

class RepositoryToGetSeller:
    def __init__(self, db_client):
        self.db = db_client

    def get_all_products(self):
        query = "SELECT id, asin FROM products_master"
        return self.db.execute_query(query)

    def get_seller_count(self, seller):
        count_query = "SELECT COUNT(*) FROM sellers WHERE seller = %s"
        return self.db.execute_query(count_query, (seller,))[0]['COUNT(*)']

    def add_seller(self, seller):
        insert_query = "INSERT INTO sellers (seller, last_search) VALUES (%s, '2020-01-01')"
        self.db.execute_update(insert_query, (seller,))

    def get_seller_id(self, seller):
        seller_id_query = "SELECT id FROM sellers WHERE seller = %s"
        return self.db.execute_query(seller_id_query, (seller,))[0]['id']

    def add_junction(self, seller_id, product_id):
        junction_query = "INSERT INTO junction (seller_id, product_id, evaluate) VALUES (%s, %s, FALSE)"
        self.db.execute_update(junction_query, (seller_id, product_id))

    def add_products_detail(self, competitors, product_id):
        update_query = "UPDATE products_detail SET competitors = %s WHERE asin_id = %s"
        self.db.execute_update(update_query, (competitors, product_id))

class RepositoryForSpAPI:
    def __init__(self, db_client):
        self.db_client = db_client
    
    def fetch_products(self):
        query = "SELECT id, asin FROM products_master WHERE weight IS NULL"
        return self.db_client.execute_query(query)

    def update_product(self, product_id, weight, weight_unit, image_url):
        query = """
            UPDATE products_master
            SET (weight, weight_unit, image_url) = (%s, %s, %s)
            WHERE id = %s
        """
        params = (weight, weight_unit, image_url, product_id)
        return self.db_client.execute_update(query, params)
    
class RepositoryToSearchImage:
    def __init__(self, db_client):
        self.db = db_client

    def get_positive_list(self):
        query = "SELECT ec_site FROM ec_sites WHERE to_research = TRUE"
        return [item['ec_site'] for item in self.db.execute_query(query)]

    def get_products_to_process(self):
        query = "SELECT id, image_url FROM products_master WHERE ec_search IS NULL AND image_url IS NOT NULL"
        return self.db.execute_query(query)

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

class RepositoryToGetSales:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_asins_without_sales_rank(self):
        query = """
            SELECT pm.asin 
            FROM products_master pm
            JOIN products_detail pd ON pm.id = pd.asin_id
            WHERE pd.three_month_sales IS NULL;
        """
        return self.db_client.execute_query(query)

    def update_sales_rank(self, asin, sales_rank_drops):
        insert_query = """
            UPDATE products_detail pd
            JOIN products_master pm ON pd.asin_id = pm.id
            SET pd.three_month_sales = %s
            WHERE pm.asin = %s;
        """
        print(asin, sales_rank_drops)
        self.db_client.execute_update(insert_query, (sales_rank_drops, asin))

class RepositoryForEvaluation:
    def __init__(self, db_client):
        self.db_client = db_client

    # is_good=NULL or Trueのidをproducts_masterから取得
    def get_products_to_evaluate(self):
        query = "SELECT id FROM products_master WHERE is_good IS NULL OR is_good = TRUE"
        return self.db_client.execute_query(query)

    # asin_idの直近3件の判定を取得
    def get_product_decisions(self, product_id):
        query = """
        SELECT decision FROM products_detail 
        WHERE asin_id = %s 
        ORDER BY id DESC 
        LIMIT 3
        """
        return self.db_client.execute_query(query, (product_id,))

    def update_product_is_good(self, product_id):
        query = "UPDATE products_master SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (product_id,))

    # is_good=NULL or Trueのidをsellersから取得
    def get_sellers_to_evaluate(self):
        query = "SELECT id FROM sellers WHERE is_good IS NULL OR is_good = TRUE"
        return self.db_client.execute_query(query)

    def get_seller_products(self, seller_id):
        query = """
        SELECT COUNT(*) as total, SUM(CASE WHEN pm.is_good = True THEN 1 ELSE 0 END) as num 
        FROM junction j JOIN products_master pm on j.product_id = pm.id 
        WHERE j.seller_id = %s
        """
        return self.db_client.execute_query(query, (seller_id,))
        
    def update_seller_is_good(self, seller_id):
        query = "UPDATE sellers SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (seller_id,))




# Managers
class AsinSearcher:
    def __init__(self, db_client, keepa_client):
        self.db_client = db_client
        self.keepa_client = keepa_client

    def process_sellers(self):
        sellers = self.db_client.get_sellers()
        for seller in sellers:
            sellerId = seller['seller']
            asins = self.keepa_client.search_asin_by_seller(sellerId)
            print(f'{sellerId} has Asins')
            for asin in asins:
                self.db_client.add_product_master(asin)
                asin_id = self.db_client.get_product_id(asin)
                if asin_id:
                    self.db_client.add_product_detail(asin_id)
                    self.db_client.write_asin_to_junction(sellerId, asin_id)

class SellerSearcher:
    def __init__(self, repository, keepa_client):
        self.repository = repository
        self.api = keepa_client

    def search_seller(self):
        products = self.repository.get_all_products()

        for product in products:
            print(f'asin : {product["asin"]}')
            asin = product['asin']
            product_id = product['id']
            seller_info = self.api.query_seller_info(asin)
            extracted_data = self.extract_info(seller_info[0]['offers'])
            print(f'extracted_data : {extracted_data}')

            if not extracted_data:
                print(f"ASIN: {asin} のsellerIDが見つかりませんでした")
                continue

            for datum in extracted_data:
                seller = datum["sellerId"]
                count = self.repository.get_seller_count(seller)

                if count == 0:
                    print(f'add sellerId : {seller}')
                    self.repository.add_seller(seller)

                seller_id = self.repository.get_seller_id(seller)
                self.repository.add_junction(seller_id, product_id)
            print(f"ASIN: {asin} のsellerIDを取得しました: {len(extracted_data)}件")

            competitors = self.count_FBA_sellers(extracted_data)
            self.repository.add_products_detail(competitors, product_id)

    def extract_info(self, data):
        result = []
        for item in data:
            if item["isFBA"] and item["condition"] == 1 and item["isShippable"] and item["isPrime"] and item["isScam"] == 0 and item["condition"] == 1:
                result.append({"sellerId": item["sellerId"], "isAmazon": item["isAmazon"], "isShippable": item["isShippable"], "isPrime": item["isPrime"]})
        return result
    
    # 未使用関数　competitorsの数を返す
    def count_FBA_sellers(self,data):
        for item in data:
            if item['isAmazon']:
                infinite = 1000
                return infinite
        prime_count = sum(1 for item in data if item['isPrime'])
        return prime_count

class AmazonProductUpdater:
    def __init__(self, db_client, api_client):
        self.db = db_client
        self.api = api_client

    def process_products(self):
        products = self.db_client.fetch_products()
        for product in products:
            product_id, asin = product['id'], product['asin']
            details = self.api.fetch_product_details(asin)

            weight = details['attributes'].get('item_package_weight', [{'value': -1}])[0]['value']
            if weight == 0 or weight == -1:
                weight = details['attributes'].get('item_weight', [{'value': -1}])[0]['value']

            weight_unit = details['attributes'].get('item_package_weight', [{'unit': ''}])[0]['unit']
            if not weight_unit:
                weight_unit = details['attributes'].get('item_weight', [{'unit': ''}])[0]['unit']

            image_url = details['images'][0]['images'][0]['link'] if details['images'] else ''

            self.db_client.update_product(product_id, weight, weight_unit, image_url)

class ImageSearchService:
    def __init__(self, repository_search_image, searcher):
        self.repository_search_image = repository_search_image
        self.searcher = searcher
    
    def process_product(self, product, positive_list):
        product_id = product['id']
        image_url = product['image_url']
        print(f'Processing product_id: {product_id}, image_url: {image_url}')

        ec_url = self.searcher.search_image(image_url, positive_list)
        print(f'Found ec_url: {ec_url}')
        
        if ec_url:
            self.repository_search_image.save_ec_url(product_id, ec_url)
            self.repository_search_image.update_product_status(product_id)
        else:
            print("No matching URL found")    

    def run(self):
        targets = self.repository_search_image.get_products_to_process()
        if len(targets) == 0:
            print("No products to process")
            return
        positive_list = self.repository_search_image.get_positive_list()
        print(f"Positive list: {positive_list}")
        for product in targets:
            print(product)
            self.process_product(product, positive_list)

class SalesRankUpdater:
    def __init__(self, db_client, keepa_client):
        self.db_client = db_client
        self.keepa_client = keepa_client

    def update_sales_ranks(self):
        asins = self.db_client.get_asins_without_sales_rank()
        for asin in asins:
            sales_rank_drops = self.keepa_client.get_sales_rank_drops(asin['asin'])
            self.db_client.update_sales_rank(asin['asin'], sales_rank_drops)

class EvaluateAsinAndSellers:
    def __init__(self, repository):
        self.repository = repository

    def evaluate_products(self):
        products = self.repository.get_products_to_evaluate()
        for product in products:
            decisions = self.repository.get_product_decisions(product['id'])
            if sum(d['decision'] for d in decisions) > 1:
                self.repository.update_product_is_good(product['id'])

    def evaluate_sellers(self):
        sellers = self.repository.get_sellers_to_evaluate()
        for seller in sellers:
            result = self.repository.get_seller_products(seller['id'])
            if result[0]['total'] == 0:
                continue
            p = result[0]['num'] / result[0]['total'] 
            print(p)
            if p > 0.3:
                self.repository.update_seller_is_good(seller['id'])


# 以下の関数は、それぞれのクラスのインスタンスを生成し、処理を実行する関数
## Keepa clientを利用する関数だけ別に分けて厳密に定期実行する？
## 利用するclientごとにFunctionsインスタンスを作成する？

# 消費token:10 per 1 seller (storefront=True:+9 tokens)
## fills products_master (asin, -last_search, -last_sellers_search), junction (seller_id, product_id, evaluate), products_detail (asin_id)
def get_asins():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    repository = RepositoryToGetAsin(db_client)
    keepa_api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = KeepaClient(keepa_api_key)
    manager = AsinSearcher(repository, keepa_client)
    try:
        manager.process_sellers()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_client.close()

# 消費token:1.6 - 6.6 per 1 asin (offers=20:+6 tokens per 10 asin)
## fills sellers (seller, last_search), junction (seller_id, product_id, evaluate), products_detail (competitors)
def get_sellers():
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }
    db_client = DatabaseClient(**db_config)
    repository = RepositoryToGetSeller(db_client)
    keepa_api_key = os.getenv("KEEPA_API_KEY")
    keepa_client = KeepaClient(keepa_api_key)
    searcher = SellerSearcher(repository, keepa_client)
    searcher.search_seller()
    db_client.close()

# 消費token:0
## fills products_master (weight, weight_unit, image_url)
def get_details():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    repository = RepositoryForSpAPI(db_client)
    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    api_client = AmazonAPIClient(**sp_credentials)
    updater = AmazonProductUpdater(repository, api_client)
    updater.process_products()
    db_client.close()

# 消費token:0
## fills products_master (ec_search), products_ec (asin_id, ec_url)
def image_search():
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }
    db_client = DatabaseClient(**db_config)
    repository = RepositoryToSearchImage(db_client)
    sercher = ImageSearcher()
    service = ImageSearchService(repository, sercher)
    service.run()
    db_client.close()

# 消費token:1 per 1 asin
## fills products_detail(three_month_sales)
def get_num_of_sales():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    repository = RepositoryToGetSales(db_client)
    api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = KeepaClient(api_key)
    sales_rank_updater = SalesRankUpdater(repository, keepa_client)
    sales_rank_updater.update_sales_ranks()

# 消費token:0
## fills products_master AND sellers (is_good)
def evaluate_asin_and_sellers():    
    db_client = DatabaseClient(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )
    repository = RepositoryForEvaluation(db_client)
    judge = EvaluateAsinAndSellers(repository)
    judge.evaluate_sellers()

## not filled : products_detail(ec_url?id, price_jpy, monthly, lowest_price, commission, deposit, expexts, decision)
## not filled : products_ec(price)
## All filled : sellers, junction, products_master, ec_sites

if __name__ == "__main__":
    print("start")
    get_sellers()