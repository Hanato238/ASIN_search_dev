import mysql.connector
import keepa
import os
import dotenv

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

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        self.cursor.execute(query, params)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

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

                junction_query = "INSERT INTO junction (seller_id, product_id, evaluate, product_master) VALUES (%s, %s, FALSE, FALSE)"
                self.db.execute_update(junction_query, (seller_id, product_id))
                # juction(created_at)の削除を今後実施
            print(f"ASIN: {asin} のsellerIDを取得しました: {len(extracted_data)}件")

    def extract_info(self, data):
        result = []
        for item in data:
            if item["isFBA"] and item["condition"] == 1 and item["isShippable"] and item["isPrime"] and item["isScam"] == 0:
                result.append({"sellerId": item["sellerId"], "isAmazon": item["isAmazon"], "isShippable": item["isShippable"], "isPrime": item["isPrime"]})
        return result

def main():
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

if __name__ == "__main__":
