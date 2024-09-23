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
    


#------------------------------------------------------------
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
                return
        
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

class SellerSearcher:
    def __init__(self, database_client, keepa_client):
        self.repository = RepositoryToGetSeller(database_client)
        self.api = keepa_client

    def process_search_seller(self, product):
        products = self.repository.get_all_products()
        for product in products:
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

def seller_searcher(database_client, keepa_client):
    return SellerSearcher(database_client, keepa_client)

#------------------------------------------------------------
class RepositoryToGetSales:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_record_without_sales_rank(self, asin_id):
        query = """
            SELECT * FROM products_detail
            WHERE asin_id = %s AND three_month_sales IS NULL;
        """
        return self.db_client.execute_query(query, (asin_id,))

    def update_sales_rank(self, record):
        id = record['id']
        three_month_sales = record['three_month_sales']
        insert_query = """
            UPDATE products_detail
            SET three_month_sales = %s
            WHERE id = %s;
        """
        self.db_client.execute_update(insert_query, (three_month_sales, id))

class SalesRankUpdater:
    def __init__(self, db_client, keepa_client):
        self.repository = RepositoryToGetSales(db_client)
        self.keepa_client = keepa_client

    def process_sales_rankd_drops(self, record):
        asin_id = record['id']
        record = self.repository.get_record_without_sales_rank(asin_id)
        record['three_month_sales'] = self.keepa_client.get_sales_rank_drops(record['asin'])
        self.repository.update_sales_rank(record)
        return record

def sales_rank_updater(database_client, keepa_client):
    return SalesRankUpdater(database_client, keepa_client)

