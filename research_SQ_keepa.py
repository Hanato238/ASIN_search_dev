import keepa
import datetime
import dotenv
import os
import pandas as pd
import mysql.connector

dotenv.load_dotenv()

class KeepaClient:
    def __init__(self, api_key):
        self.api = keepa.Keepa(api_key)

    def query_product(self, asin):
        return self.api.query(asin, domain='JP', history=True, offers=20, only_live_offers=True)

class DatabaseClient:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def fetch_asins_with_null_sales(self):
        query = """
        SELECT asin FROM products_master
        WHERE tms_test2 IS NULL
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [result[0] for result in results]
    
    def update_three_month_sales(self, count, asin):
        update_query = """
        UPDATE products_master
        SET tms_test2 = %s
        WHERE asin = %s
        """
        self.cursor.execute(update_query, (count, asin))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

class KeepaSalesAnalyzer:
    def __init__(self, keepa_client):
        self.keepa_client = keepa_client
        self.now = datetime.datetime.now()

    def keepa_time_to_unix(self, keepa_time):
        return (keepa_time + 21564000) * 60

    def unix_to_datetime(self, unix_time):
        return datetime.datetime.utcfromtimestamp(unix_time)

    def filter_last_90_days(self, data):
        filtered_data = []
        for i in range(0, len(data), 2):
            keepa_time = data[i]
            sales_rank = data[i + 1]
            unix_time = self.keepa_time_to_unix(keepa_time)
            date_time = self.unix_to_datetime(unix_time)
            if self.now - datetime.timedelta(days=90) <= date_time <= self.now:
                filtered_data.append((date_time, sales_rank))
        return filtered_data

    def analyze_sales(self, asin):
        products = self.keepa_client.query_product(asin)
        saleRanks = products[0]['salesRanks']
        if saleRanks == None:
            return 0
        else:
            first_key = next(iter(saleRanks))
        data = products[0]['salesRanks'][first_key]
        data = self.filter_last_90_days(data)
        df = pd.DataFrame(data, columns=['date', 'rank'])
        df['rank_change'] = df['rank'].pct_change() * 100
        p = 5  # 例として5%を使用
        count = (df['rank_change'] < -p).sum()
        return int(count)

class DatabaseUpdater:
    def __init__(self, db_client, keepa_analyzer):
        self.db_client = db_client
        self.keepa_analyzer = keepa_analyzer

    def update_three_month_sales(self):
        results = self.db_client.fetch_asins_with_null_sales()
        print(results)
        for asin in results:
            count = self.keepa_analyzer.analyze_sales(asin)
            self.db_client.update_three_month_sales(count, asin)

if __name__ == "__main__":
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    api_key = os.getenv('KEEPA_API_KEY')

    keepa_client = KeepaClient(api_key)
    db_client = DatabaseClient(**db_config)
    keepa_analyzer = KeepaSalesAnalyzer(keepa_client)
    updater = DatabaseUpdater(db_client, keepa_analyzer)

    updater.update_three_month_sales()
    db_client.close()
