import mysql.connector as mydb
import keepa
import os
import dotenv
import datetime

dotenv.load_dotenv()

class Database:
    def __init__(self):
        self.db = mydb.connect(
            host="localhost",
            port="3306",
            user="root",
            password="mysql",
            database="test"
        )
        self.cursor = self.db.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        self.cursor.execute(query, params)
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()

class KeepaAPI:
    def __init__(self):
        keepa_api_key = os.getenv("KEEPA_API_KEY")
        self.api = keepa.Keepa(keepa_api_key)

    def query_seller_info(self, asin_code):
        return self.api.query(asin_code, domain='JP', history=False, offers=20, only_live_offers=True)

class SellerSearcher:
    def __init__(self, db, api):
        self.db = db
        self.api = api

    def search_seller(self):
        query = "SELECT id, asin FROM products_master"
        products = self.db.execute_query(query)

        for product in products:
            print(f'asin : {product["asin"]}')
            asin_code = product['asin']
            product_id = product['id']
            seller_info = self.api.query_seller_info(asin_code)
            extracted_data = self.extract_info(seller_info[0]['offers'])
            print(f'extracted_data : {extracted_data}')

            for datum in extracted_data:
                seller = datum["sellerId"]
                count_query = "SELECT COUNT(*) FROM sellers WHERE seller = %s"
                count = self.db.execute_query(count_query, (seller,))[0]['COUNT(*)']
                print(f'count : {count}')

                if count == 0:
                    print(f'sellerId : {seller}')
                    insert_query = "INSERT INTO sellers (seller, last_search) VALUES (%s, '2020-01-01')"
                    self.db.execute_update(insert_query, (seller,))

                seller_id_query = "SELECT id FROM sellers WHERE seller = %s"
                seller_id = self.db.execute_query(seller_id_query, (seller,))[0]['id']

                junction_query = "INSERT INTO junction (seller_id, product_id, evaluate, product_master, created_at) VALUES (%s, %s, FALSE, FALSE, NOW())"
                self.db.execute_update(junction_query, (seller_id, product_id))
                # juction(created_at)の削除を今後実施
            print(f"ASIN: {asin_code} のsellerIDを取得しました: {len(extracted_data)}件")

    def extract_info(self, data):
        result = []
        for item in data:
            if item["isFBA"] and item["condition"] == 1 and item["isShippable"] and item["isPrime"] and item["isScam"] == 0:
                result.append({"sellerId": item["sellerId"], "isAmazon": item["isAmazon"], "isShippable": item["isShippable"], "isPrime": item["isPrime"]})
        return result

if __name__ == "__main__":
    db = Database()
    api = KeepaAPI()
    searcher = SellerSearcher(db, api)
    searcher.search_seller()
    db.close()
