import keepa
import dotenv
import os
import mysql.connector

class KeepaClient:
    def __init__(self):
        self.api_key = os.getenv("KEEPA_API_KEY")
        self.api = keepa.Keepa(self.api_key)

    def get_sales_rank_drops(self, asin):
        products = self.api.query(asin, domain='JP', stats=90)
        return products[0]['stats']['salesRankDrops90']

    def search_asin_by_seller(self, seller):
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            return products[seller]['asinList']
        except Exception as e:
            print(f"Error fetching ASINs for seller {seller}: {e}")
            return []

class DatabaseClient:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

def main():
    dotenv.load_dotenv()

    keepa_client = KeepaClient()
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)

    asins = db_client.execute_query("""
        SELECT pm.asin
        FROM products_detail pd
        JOIN research r ON pd.research_id = r.id
        JOIN products_master pm ON r.asin_id = pm.id
    """)

    for asin in asins:
        sales_rank_drops = keepa_client.get_sales_rank_drops(asin[0])
        db_client.execute_query("""
            UPDATE products_detail
            SET three_month_sales = %s
            WHERE research_id = (
                SELECT id FROM products_master WHERE asin = %s
            )
        """, (sales_rank_drops, asin[0]))
        db_client.commit()

    db_client.close()

if __name__ == "__main__":
    main()
