import keepa
import dotenv
import logging
from typing import List, Dict, Any, Optional

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class KeepaClient:
    _instance = None

    def __new__(cls, api_key: str) -> 'KeepaClient':
        if cls._instance is None:
            cls._instance = super(KeepaClient, cls).__new__(cls)
            cls._instance.api = keepa.Keepa(api_key)
        return cls._instance
    
    def _initialize(self, api_key: str) -> None:
        self.api = keepa.Keepa(api_key)
        self.api._timeout = 20

    def search_asin_by_seller(self, seller: str) -> List[str]:
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            return products[seller]['asinList']
        except Exception as e:
            logging.error(f"Error fetching ASINs for seller {seller}: {e}")
            return []
        
    def query_seller_info(self, asin: str) -> Dict[str, Any]:
        return self.api.query(asin, domain='JP', history=False, offers=20, only_live_offers=True)
    '''
        this returns data
        1. data[0][['offers'] : market place object　: read "https://keepa.com/#!discuss/t/marketplace-offer-object/807"
            {
                "offerId": Integer,
                "lastSeen": Integer,
                "sellerId": String,
                "isPrime": Boolean,
                "isFBA": Boolean,
                "isMAP": Boolean,
                "isShippable": Boolean,
                "isAddonItem": Boolean,
                "isPreorder": Boolean,
                "isWarehouseDeal": Boolean,
                "isScam": Boolean,
                "shipsFromChina": Boolean,
                "isAmazon": Boolean,
                "isPrimeExcl": Boolean,
                "coupon": Integer,
                "couponHistory": Integer array,
                "condition": Integer,
                "minOrderQty": Integer,
                "conditionComment": String,
                "offerCSV": Integer array,
                "stockCSV": Integer array,
                "primeExclCSV": Integer array
            }
    '''
    def get_sales_rank_drops(self, asin: str) -> int:
        products = self.api.query(asin, domain='JP', stats=90)
        return products[0]['stats']['salesRankDrops90']
    
def keepa_client(api_key: str) -> KeepaClient:
    return KeepaClient(api_key)

#------------------------------------------------------------
class RepositoryToGetAsin:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_sellers(self):
        return self.db_client.execute_query("SELECT seller FROM sellers")[0]

    def add_product_master(self, asin):
        counts = self.db_client.execute_query("SELECT COUNT(*) FROM products_master WHERE asin = %s", (asin,))
        if counts[0]['COUNT(*)'] == 0:
            insert_query = """
                INSERT INTO products_master (asin, last_search)
                VALUES (%s, '2020-01-01')
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
            INSERT INTO junction (seller_id, product_id)
            VALUES (%s, %s)
        """
        self.db_client.execute_update(insert_query, (seller_id, product_id))

    def add_product_detail(self, asin_id):
        insert_query = """
            INSERT INTO products_detail (asin_id)
            VALUE (%s)
        """
        self.db_client.execute_update(insert_query, (asin_id,))

def repository_to_get_asin(database_client):
    return RepositoryToGetAsin(database_client)
# api.query()がFacadeパターンではRuntime Errorになる
class AsinSearcher:
    def __init__(self, db_client, keepa_client):
        self.repository = RepositoryToGetAsin(db_client)
        self.keepa_client = keepa_client

    def process_seller(self):
        sellers = self.repository.get_sellers()
        for seller in sellers:
            asins = self.keepa_client.search_asin_by_seller(seller)
            if len(asins) == 0:
                print(f'{seller} has NO Asins')
                continue
        
            print(f'{seller} has Asins')
            for asin in asins:
                self.repository.add_product_master(asin)
                asin_id = self.repository.get_product_id(asin)
                if asin_id:
                    self.repository.add_product_detail(asin_id)
                    self.repository.write_asin_to_junction(seller, asin_id)

def asin_searcher(db_client, keepa_client):
    return AsinSearcher(db_client, keepa_client)


#------------------------------------------------------------
class RepositoryToGetSeller:
    def __init__(self, db_client: Any) -> None:
        self.db = db_client

    def get_products_to_process(self) -> List[Dict[str, Any]]:
        query = "SELECT id, asin FROM products_master WHERE is_good IS NULL OR is_good = TRUE"
        try:
            return self.db.execute_query(query)
        except Exception as e:
            logging.error(f"Error fetching all products: {e}")
            return []

    def get_seller_count(self, seller: str) -> int:
        count_query = "SELECT COUNT(*) FROM sellers WHERE seller = %s"
        try:
            return self.db.execute_query(count_query, (seller,))[0]['COUNT(*)']
        except Exception as e:
            logging.error(f"Error fetching seller count: {e}")
            return 0
            
    def add_seller(self, seller: str) -> None:
        insert_query = "INSERT INTO sellers (seller) VALUES (%s)"
        self.db.execute_update(insert_query, (seller,))

    def get_seller_id(self, seller: str) -> int:
        seller_id_query = "SELECT id FROM  sellers WHERE seller = %s"
        try:
            return self.db.execute_query(seller_id_query, (seller,))[0]['id']
        except Exception as e:
            logging.error(f"Error fetching seller ID: {e}")
            return None
        
    def add_junction(self, seller_id: int, product_id: int) -> None:
        junction_query = "INSERT INTO junction (seller_id, product_id) VALUES (%s, %s)"
        try:
            self.db.execute_update(junction_query, (seller_id, product_id))
        except Exception as e:
            logging.error(f"Error adding junction for seller_id {seller_id} and product_id {product_id}: {e}")

    def create_record_to_products_detail(self, product_id: int, competitors: int) -> None:
        query = "INSERT INTO products_detail (asin_id, competitors) VALUES (%s, %s)"
        try:
            self.db.execute_update(query, (product_id, competitors))
        except Exception as e:
            logging.error(f"Error creating record for product_id {product_id}: {e}")

class SellerSearcher:
    def __init__(self, database_client: Any, keepa_client: Any) -> None:
        self.repository = RepositoryToGetSeller(database_client)
        self.api = keepa_client

    def process_search_seller(self) -> None:
        products = self.repository.get_products_to_process()
        for product in products:
            print(f'asin : {product["asin"]}')
            asin = product['asin']
            product_id = product['id']
            seller_info = self.api.query_seller_info(asin)
            extracted_data = self.extract_info(seller_info[0]['offers'])

            competitors = self.count_FBA_sellers(extracted_data)
            self.repository.create_record_to_products_detail(product_id, competitors)

            if not extracted_data:
                logging.info(f"ASIN: {asin} のsellerIDが見つかりませんでした")
                return

            for datum in extracted_data:
                seller = datum["sellerId"]
                count = self.repository.get_seller_count(seller)

                if count == 0:
                    logging.info(f'add sellerId : {seller}')
                    self.repository.add_seller(seller)

                seller_id = self.repository.get_seller_id(seller)
                self.repository.add_junction(seller_id, product_id)
            logging.info(f"ASIN: {asin} のsellerIDを取得しました: {len(extracted_data)}件")

    def extract_info(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]: 
        result = []
        for item in data:
            if item["isFBA"] and item["condition"] == 1 and item["isShippable"] and item["isPrime"] and item["isScam"] == 0 and item["condition"] == 1:
                result.append({"sellerId": item["sellerId"], "isAmazon": item["isAmazon"], "isShippable": item["isShippable"], "isPrime": item["isPrime"]})
        return result
    
    def count_FBA_sellers(self, data: List[Dict[str, Any]]) -> int:
        # Check if any element has isAmazon set to True
        for item in data:
            if item['isAmazon']:
                return 1000
    
        # Count elements where isPrime is True
        prime_count = sum(1 for item in data if item['isPrime'])
        return prime_count

# これはFacadeパターンでも機能する
def seller_searcher(database_client: Any, keepa_client: Any) -> SellerSearcher:
    return SellerSearcher(database_client, keepa_client)

#------------------------------------------------------------
class RepositoryToGetSales:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_record_to_process(self):
        query = """
            SELECT pd.* FROM products_detail pd
            JOIN products_master pm ON pd.asin_id = pm.id
            WHERE pd.three_month_sales IS NULL;
        """
        records = self.db_client.execute_query(query)
        return records
    
    def get_asin_from_product_detail(self, product_id):
        query = """
            SELECT pm.asin
            FROM products_detail pd
            JOIN products_master pm ON pd.asin_id = pm.id
            WHERE pd.id = %s;
            """
        #query = "SELECT asin_id FROM products_detail WHERE id = %s"
        return self.db_client.execute_query(query, (product_id,))[0]
    
    def update_sales_rank(self, record):
        id = record['id']
        three_month_sales = record['three_month_sales']
        insert_query = """
            UPDATE products_detail
            SET three_month_sales = %s
            WHERE id = %s;
        """
        self.db_client.execute_update(insert_query, (three_month_sales, id))

class DetailUpdater:
    def __init__(self, db_client, keepa_client):
        self.repository = RepositoryToGetSales(db_client)
        self.keepa_client = keepa_client

    def get_record_to_process(self):
        records = self.repository.get_record_to_process()
        return records

    def process_sales_rank_drops(self, record):
        try:
            asin = self.repository.get_asin_from_product_detail(record['id'])
            record['three_month_sales'] = self.keepa_client.get_sales_rank_drops(asin['asin'])
            self.repository.update_sales_rank(record)
            return record
        except Exception as e:
            print(f"Error processing sales rank drops for record {record['asin']}: {e}")
            return None

    def process_get_competitors(self, record):
        try:
            asin = self.repository.get_asin_from_product_detail(record['id'])
            seller_info = self.keepa_client.api.query_seller_info(asin)
            extracted_data = self.extract_info(seller_info[0]['offers'])
            competitors = self.count_FBA_sellers(extracted_data)
            record[0]['competitors'] = competitors
        except Exception as e:
            print(f"Error processing competitors for record {record['id']}: {e}")

    def count_FBA_sellers(self, data):
        try:
            # Check if any element has isAmazon set to True
            for item in data:
                if item['isAmazon']:
                    return 1000

            # Count elements where isPrime is True
            prime_count = sum(1 for item in data if item['isPrime'])
            return prime_count
        except Exception as e:
            print(f"Error counting FBA sellers: {e}")
            return 0

def detail_updater(database_client, keepa_client):
    return DetailUpdater(database_client, keepa_client)

