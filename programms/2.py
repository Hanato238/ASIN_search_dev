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

if __name__ == "__main__":
    db = Database()
    api = KeepaAPI()
    asin = "B07BFH96M3"
    seller_info = api.query_seller_info(asin)
    print(seller_info)
    db.close()