import keepa
import dotenv
import os
import mysql.connector

class KeepaClient:
    def __init__(self, api_key):
        self.api = keepa.Keepa(api_key)

    def get_sales_rank_drops(self, asin):
        products = self.api.query(asin, domain='JP', stats=90)
        return products[0]['stats']['salesRankDrops90']

class DatabaseClient:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def get_asins(self):
        query = """
        SELECT pm.asin
        FROM products_detail pd
        JOIN research r ON pd.research_id = r.id
        JOIN products_master pm ON r.asin_id = pm.id
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def update_three_month_sales(self, asin, sales_rank_drops):
        self.cursor.execute("""
            UPDATE products_detail
            SET three_month_sales = %s
            WHERE research_id = (
                SELECT id FROM products_master WHERE asin = %s
            )
        """, (sales_rank_drops, asin))
        self.connection.commit()

def main():
    dotenv.load_dotenv()
    api_key = os.getenv('KEEPA_API_KEY')
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }

    keepa_client = KeepaClient(api_key)
    db_client = DatabaseClient(**db_config)

    asins = db_client.get_asins()
    for asin in asins:
        sales_rank_drops = keepa_client.get_sales_rank_drops(asin)
        db_client.update_three_month_sales(asin, sales_rank_drops)

if __name__ == "__main__":
    main()
