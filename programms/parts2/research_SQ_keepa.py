import keepa
import dotenv
import os
import mysql.connector

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

# !! これは3カ月間販売数しか取得していない！
class KeepaClient:
    def __init__(self, api_key):
        self.api = keepa.Keepa(api_key)

    def get_sales_rank_drops(self, asin):
        products = self.api.query(asin, domain='JP', stats=90)
        return products[0]['stats']['salesRankDrops90']

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


    
class SalesRankUpdater:
    def __init__(self, db_client, keepa_client):
        self.db_client = db_client
        self.keepa_client = keepa_client

    def update_sales_rank(self, asin):
        sales_rank_drops = self.keepa_client.get_sales_rank_drops(asin)
        self.db_client.update_sales_rank(asin, sales_rank_drops)

def main():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    repository = RepositoryToGetSales(db_client)
    api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = KeepaClient(api_key)

    sales_rank_updater = SalesRankUpdater(repository, keepa_client)
    asins = repository.get_asins_without_sales_rank()
    for asin in asins:
        sales_rank_updater.update_sales_rank(asin['asin'])

if __name__ == "__main__":
    main()