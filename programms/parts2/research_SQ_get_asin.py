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

def main():
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
        sellers = repository.get_sellers()
        for seller in sellers:
            manager.process_seller(seller)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_client.close()

if __name__ == "__main__":
    main()
