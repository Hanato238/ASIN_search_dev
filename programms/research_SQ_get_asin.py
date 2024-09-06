import mysql.connector as mydb
import keepa
import os
import dotenv

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
        self.cursor = self.db.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def commit(self):
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()

class KeepaAPI:
    def __init__(self):
        self.api_key = os.getenv("KEEPA_API_KEY")
        self.api = keepa.Keepa(self.api_key)

    def search_asin_by_seller(self, seller):
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            return products[seller]['asinList']
        except Exception as e:
            print(f"Error fetching ASINs for seller {seller}: {e}")
            return []

class SellerManager:
    def __init__(self, db, api):
        self.db = db
        self.api = api

    def get_sellers(self):
        return self.db.execute_query("SELECT seller FROM sellers")

    def add_product_master(self, asin):
        count = self.db.execute_query("SELECT COUNT(*) FROM products_master WHERE asin = %s", (asin,))[0][0]
        if count == 0:
            self.db.execute_query("""
                INSERT INTO products_master (asin, last_search, last_sellers_search)
                VALUES (%s, '2020-01-01', '2020-01-01')
            """, (asin,))
            self.db.commit()

    def get_product_id(self, asin):
        result = self.db.execute_query("SELECT id FROM products_master WHERE asin = %s", (asin,))
        return result[0][0] if result else None

    def write_asin_to_junction(self, seller, product_id):
        try:
            seller_id = self.db.execute_query("SELECT id FROM sellers WHERE seller = %s", (seller,))[0][0]
            self.db.execute_query("""
                INSERT INTO junction (seller_id, product_id, evaluate, product_master)
                VALUES (%s, %s, %s, %s)
            """, (seller_id, product_id, False, True))
            self.db.commit()
        except mydb.Error as err:
            print(f"Error: {err}")

    def process_sellers(self):
        sellers = self.get_sellers()
        for seller in sellers:
            asins = self.api.search_asin_by_seller(seller[0])
            print(f'{seller[0]} has Asins')
            for asin in asins:
                self.add_product_master(asin)
                product_id = self.get_product_id(asin)
                if product_id:
                    self.write_asin_to_junction(seller[0], product_id)

def main():
    db = Database()
    api = KeepaAPI()
    manager = SellerManager(db, api)
    try:
        manager.process_sellers()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
