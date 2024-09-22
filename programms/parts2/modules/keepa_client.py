import keepa
import os
import dotenv

dotenv.load_dotenv()

class KeepaClient:
    def __init__(self, api_key):
        self.api = keepa.Keepa(api_key)

    def search_asin_by_seller(self, seller):
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            return products[seller]['asinList']
        except Exception as e:
            print(f"Error fetching ASINs for seller {seller}: {e}")
            return []
        
    def query_seller_info(self, asin):
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
    def get_sales_rank_drops(self, asin):
        products = self.api.query(asin, domain='JP', stats=90)
        return products[0]['stats']['salesRankDrops90']
    
class AsinSearcher:
    def __init__(self, db_client, keepa_client):
        self.db_client = db_client
        self.keepa_client = keepa_client

    def process_seller(self, seller):
        sellerId = seller['seller']
        asins = self.keepa_client.search_asin_by_seller(sellerId)
        if len(asins) == 0:
            print(f'{sellerId} has NO Asins')
            return
        
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

    def search_seller(self, product):
        print(f'asin : {product["asin"]}')
        asin = product['asin']
        product_id = product['id']
        seller_info = self.api.query_seller_info(asin)
        extracted_data = self.extract_info(seller_info[0]['offers'])

        competitors = self.count_FBA_sellers(extracted_data)
        self.repository.create_record_to_products_detail(product_id, competitors)

        if not extracted_data:
            print(f"ASIN: {asin} のsellerIDが見つかりませんでした")
            return

        for datum in extracted_data:
            seller = datum["sellerId"]
            count = self.repository.get_seller_count(seller)

            if count == 0:
                print(f'add sellerId : {seller}')
                self.repository.add_seller(seller)

            seller_id = self.repository.get_seller_id(seller)
            self.repository.add_junction(seller_id, product_id)
        print(f"ASIN: {asin} のsellerIDを取得しました: {len(extracted_data)}件")

    def extract_info(self, data):
        result = []
        for item in data:
            if item["isFBA"] and item["condition"] == 1 and item["isShippable"] and item["isPrime"] and item["isScam"] == 0 and item["condition"] == 1:
                result.append({"sellerId": item["sellerId"], "isAmazon": item["isAmazon"], "isShippable": item["isShippable"], "isPrime": item["isPrime"]})
        return result
    
    def count_FBA_sellers(self, data):
        # Check if any element has isAmazon set to True
        for item in data:
            if item['isAmazon']:
                return 1000
    
        # Count elements where isPrime is True
        prime_count = sum(1 for item in data if item['isPrime'])
        return prime_count

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


    
def keepa_client(api_key):
    return KeepaClient(api_key)

def asin_searcher(db_client, keepa_client=KeepaClient(os.getenv('KEEPA_API_KEY'))):
    return AsinSearcher(db_client, keepa_client)

def seller_searcher(repository, keepa_client=KeepaClient(os.getenv('KEEPA_API_KEY'))):
    return SellerSearcher(repository, keepa_client)

def sales_rank_updater(db_client, keepa_client=KeepaClient(os.getenv('KEEPA_API_KEY'))):
    return SalesRankUpdater(db_client, keepa_client)

class RepositoryToGetSeller:
    def __init__(self, db_client):
        self.db = db_client

    def get_all_products(self):
        query = "SELECT id, asin FROM products_master WHERE is_good IS NULL OR is_good = TRUE"
        return self.db.execute_query(query)

    def get_seller_count(self, seller):
        count_query = "SELECT COUNT(*) FROM sellers WHERE seller = %s"
        return self.db.execute_query(count_query, (seller,))[0]['COUNT(*)']

    def add_seller(self, seller):
        insert_query = "INSERT INTO sellers (seller) VALUES (%s)"
        self.db.execute_update(insert_query, (seller,))

    def get_seller_id(self, seller):
        seller_id_query = "SELECT id FROM sellers WHERE seller = %s"
        return self.db.execute_query(seller_id_query, (seller,))[0]['id']

    def add_junction(self, seller_id, product_id):
        junction_query = "INSERT INTO junction (seller_id, product_id) VALUES (%s, %s)"
        self.db.execute_update(junction_query, (seller_id, product_id))

    def create_record_to_products_detail(self, product_id, competitors):
        query = "INSERT INTO products_detail (asin_id, competitors) VALUES (%s, %s)"
        self.db.execute_update(query, (product_id, competitors))

def repository_to_get_seller(db_client):
    return RepositoryToGetSeller(db_client)

class RepositoryToGetAsin:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_sellers(self):
        return self.db_client.execute_query("SELECT seller FROM sellers")

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

def repository_to_get_asin(db_client):
    return RepositoryToGetAsin(db_client)

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

def repository_to_get_sales(db_client):
    return RepositoryToGetSales(db_client)