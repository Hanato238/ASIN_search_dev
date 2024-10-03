import keepa
import dotenv

from modules.Repository.repository.py import repsoitory_for_sellers, repository_for_junction, repository_for_products_master, repository_for_products_detail

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
        self.api = keepa.Keepa(api_key, timeout=30)

    def search_asin_by_seller(self, seller: str) -> List[str]:
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            if seller not in products:
                logging.info(f"ASINs not found for seller {seller}")
                return []
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
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def get_sellers(self) -> List[Dict[str, Any]]:
        logging.info("Fetching sellers")
        sellers = self.db_client.execute_query("SELECT seller FROM sellers")
        logging.info(f"Fetched {len(sellers)} sellers")
        return sellers

    def add_product_master(self, asin: str) -> None:
        logging.info("Adding product master")
        counts = self.db_client.execute_query("SELECT COUNT(*) FROM products_master WHERE asin = %s", (asin,))
        if counts[0]['COUNT(*)'] == 0:
            insert_query = """
                INSERT INTO products_master (asin, last_search)
                VALUES (%s, '2020-01-01')
            """
            self.db_client.execute_update(insert_query, (asin,))
            logging.info(f"Added product master for ASIN: {asin}")
        else:
            logging.info(f"Product master for ASIN: {asin} already exists")

    def get_product_id(self, asin: str) -> Optional[int]:
        logging.info(f"Fetching product ID for ASIN: {asin}")
        result = self.db_client.execute_query("SELECT id FROM products_master WHERE asin = %s", (asin,))
        product_id = result[0]['id'] if result else None
        logging.info(f"Fetched product ID: {product_id} of ASIN: {asin}")
        return product_id
    
    def get_junction(self, seller: str, product_id: int) -> Optional[Dict[str, Any]]:   
        logging.info(f"Fetching junction for seller: {seller} and product ID: {product_id}")
        query = """
            SELECT COUNT(*) FROM junction
            WHERE seller_id = (SELECT id FROM sellers WHERE seller = %s)
            AND product_id = %s
        """
        result = self.db_client.execute_query(query, (seller, product_id))
        junction = result[0]['COUNT(*)'] if result else None
        logging.info(f"Fetched junction for seller: {seller} and product ID: {product_id}")
        return junction

    def write_asin_to_junction(self, seller: str, product_id: int) -> None:
        logging.info(f"Writing ASIN to junction for seller: {seller} and product ID: {product_id}")
        query = "SELECT id FROM sellers WHERE seller = %s"
        seller_id = self.db_client.execute_query(query, (seller,))[0]['id']
        insert_query = """
            INSERT INTO junction (seller_id, product_id)
            VALUES (%s, %s)
        """
        self.db_client.execute_update(insert_query, (seller_id, product_id))
        logging.info(f"Written ASIN to junction for seller: {seller} and product ID: {product_id}")

    def add_product_detail(self, asin_id: int) -> None:
        logging.info("Adding product detail for ASIN ID: {asin_id}")
        insert_query = """
            INSERT INTO products_detail (asin_id)
            VALUE (%s)
        """
        self.db_client.execute_update(insert_query, (asin_id,))
        logging.info(f"Added product detail for ASIN ID: {asin_id}")

def repository_to_get_asin(database_client: Any) -> RepositoryToGetAsin:
    return RepositoryToGetAsin(database_client)

class AsinSearcher:
    def __init__(self, db_client: Any, keepa_client: Any) -> None:
        self.repository = RepositoryToGetAsin(db_client)
        self.keepa_client = keepa_client

    def process_seller(self) -> None:
        logging.info("Starting seller processing")
        sellers = self.repository.get_sellers()
        for seller in sellers:
            seller = seller['seller']
            logging.info(f"Processing seller: {seller}")
            asins = self.keepa_client.search_asin_by_seller(seller)
            if len(asins) == 0:
                logging.info(f'{seller} has NO Asins')
                continue
        
            logging.info(f'{seller} has Asins')
            for asin in asins:
                self.repository.add_product_master(asin)
                asin_id = self.repository.get_product_id(asin)
                if asin_id:
                    self.repository.add_product_detail(asin_id)
                    if self.repository.get_junction(seller, asin_id):
                        logging.info(f"ASIN: {asin} already exists in junction for seller: {seller}")
                    else:
                        self.repository.write_asin_to_junction(seller, asin_id)
        logging.info("Seller processing complete")

def asin_searcher(db_client: Any, keepa_client: Any) -> AsinSearcher:
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
class RepositoryToGetSalesToGet:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    # products_ecとproducts_masterがいずれもfilledなasinが必要・・・
    def get_record_to_process(self) -> List[Dict[str, Any]]:
        logging.info("Fetching records to process")
        query = """
            SELECT * FROM products_detail WHERE is_researched IS NULL;
        """
        records = self.db_client.execute_query(query)
        logging.info(f"Fetched {len(records)} records to process")
        return records
    
    def get_asin_from_product_detail(self, product_id: int) -> Dict[str, Any]:
        logging.info(f"Fetching ASIN from product detail for product ID: {product_id}")
        query = """
            SELECT pm.asin
            FROM products_detail pd
            JOIN products_master pm ON pd.asin_id = pm.id
            WHERE pd.id = %s;
            """
        #query = "SELECT asin_id FROM products_detail WHERE id = %s"
        return self.db_client.execute_query(query, (product_id,))[0]
    
class RepositoryToGetSalesToUpdate:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def update_sales_rank(self, record: Dict[str, Any]) -> None:
        logging.info(f"Updating sales rank for record {record['id']}")
        id = record['id']
        three_month_sales = record['three_month_sales']
        insert_query = """
            UPDATE products_detail
            SET three_month_sales = %s
            WHERE id = %s;
        """
        self.db_client.execute_update(insert_query, (three_month_sales, id))
        logging.info(f"Updated sales rank for record {record['id']}")

    def update_competitors(self, record: Dict[str, Any]) -> None:
        logging.info(f"Updating competitors for record_id: {record['id']}")
        id = record['id']
        competitors = record['competitors']
        insert_query = """
            UPDATE products_detail
            SET competitors = %s
            WHERE id = %s;
        """
        self.db_client.execute_update(insert_query, (competitors, id))
        logging.info(f"Updated competitors for record {record['id']}")

    def update_detail_status(self, record: Dict[str, Any]) -> None:
        logging.info(f"Updating detail status for record {record['id']}")
        id = record['id']
        insert_query = """
            UPDATE products_detail
            SET is_researched = TRUE
            WHERE id = %s;
        """
        self.db_client.execute_update(insert_query, (id,))
        logging.info(f"Updated detail status for record {record['id']}")

class DetailUpdater:
    def __init__(self, db_client: Any, keepa_client: Any) -> None:
        self.get = RepositoryToGetSalesToGet(db_client)
        self.update = RepositoryToGetSalesToUpdate(db_client)
        self.keepa_client = keepa_client

    def get_record_to_process(self) -> List[Dict[str, Any]]:
        records = self.get.get_record_to_process()
        return records
    
    def update_detail_status(self, record: Dict[str, Any]) -> None:
        try:
            self.update.update_detail_status(record)
        except Exception as e:
            logging.error(f"Error updating detail status for record {record['id']}: {e}")

    def process_sales_rank_drops(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            asin = self.get.get_asin_from_product_detail(record['id'])
            record['three_month_sales'] = self.keepa_client.get_sales_rank_drops(asin['asin'])
            self.update.update_sales_rank(record)
            return record
        except Exception as e:
            print(f"Error processing sales rank drops for record {record['asin']}: {e}")
            return None

    def process_get_competitors(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            asin = self.get.get_asin_from_product_detail(record['id'])
            seller_info = self.keepa_client.query_seller_info(asin['asin'])
            extracted_data = self.extract_info(seller_info[0]['offers'])
            competitors = self.count_FBA_sellers(extracted_data)
            record['competitors'] = competitors
            self.update.update_competitors(record)
            return record
        except Exception as e:
            logging.error(f"Error processing competitors for record {record['id']}: {e}")
            return None

    def extract_info(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]: 
        result = []
        for item in data:
            if item["isFBA"] and item["condition"] == 1 and item["isShippable"] and item["isPrime"] and item["isScam"] == 0 and item["condition"] == 1:
                result.append({"sellerId": item["sellerId"], "isAmazon": item["isAmazon"], "isShippable": item["isShippable"], "isPrime": item["isPrime"]})
        return result
    
    def count_FBA_sellers(self, data: List[Dict[str, Any]]) -> int:
        try:
            if not data:
                logging.info("No data found")
                return 0
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

def detail_updater(database_client: Any, keepa_client: Any) -> DetailUpdater:
    return DetailUpdater(database_client, keepa_client)

