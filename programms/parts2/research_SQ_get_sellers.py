import mysql.connector
import keepa
import os
import dotenv

import modules.database_client as db
import modules.keepa_client as keepa

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

def main():
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }
    db_client = db.database_client(**db_config)

    repository = RepositoryToGetSeller(db_client)

    keepa_api_key = os.getenv("KEEPA_API_KEY")
    keepa_client = keepa.keepa(keepa_api_key)
    searcher = keepa.seller_searcher(db_client, keepa_client)

    searcher.process_search_seller()

    db_client.close()

if __name__ == "__main__":
    main()