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
        self.cursor.execute(query, params or ())
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


class SellerManager:
    def __init__(self, db_client, keepa_client):
        self.db_client = db_client
        self.keepa_client = keepa_client

    def get_sellers(self):
        return self.db_client.execute_query("SELECT seller FROM sellers")

    def add_product_master(self, asin):
        count = self.db_client.execute_query("SELECT COUNT(*) FROM products_master WHERE asin = %s", (asin,))[0][0]
        if count == 0:
            self.db_client.execute_query("""
                INSERT INTO products_master (asin, last_search, last_sellers_search)
                VALUES (%s, '2020-01-01', '2020-01-01')
            """, (asin,))
        # 追加でproducts_detailにid, asinのみのレコードを追加する

    def get_product_id(self, asin):
        result = self.db_client.execute_query("SELECT id FROM products_master WHERE asin = %s", (asin,))
        return result[0][0] if result else None

    def write_asin_to_junction(self, seller, product_id):
        try:
            seller_id = self.db_client.execute_query("SELECT id FROM sellers WHERE seller = %s", (seller,))[0][0]
            self.db_client.execute_query("""
                INSERT INTO junction (seller_id, product_id, evaluate, product_master)
                VALUES (%s, %s, %s, %s)
            """, (seller_id, product_id, False, True))
            self.db_client.execute_update()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def process_sellers(self):
        sellers = self.get_sellers()
        for seller in sellers:
            asins = self.keepa_client.search_asin_by_seller(seller[0])
            print(f'{seller[0]} has Asins')
            for asin in asins:
                self.add_product_master(asin)
                product_id = self.get_product_id(asin)
                if product_id:
                    self.write_asin_to_junction(seller[0], product_id)

def main():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    keepa_api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = KeepaClient(keepa_api_key)
    manager = SellerManager(db_client, keepa_client)
    try:
        manager.process_sellers()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_client.close()

if __name__ == "__main__":
    main()
