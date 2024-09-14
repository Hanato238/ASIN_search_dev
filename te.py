import time
import dotenv
import os
from sp_api.api import CatalogItems
import mysql.connector
from sp_api.base.exceptions import SellingApiRequestThrottledException

dotenv.load_dotenv()

class Database:
    def __init__(self):
        self.db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
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

class AmazonProductUpdater:
    def __init__(self, db):
        self.credentials = {
            'refresh_token': os.getenv('REFRESH_TOKEN'),
            'lwa_app_id': os.getenv('LWA_APP_ID'),
            'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET')
        }
        self.marketplace = os.getenv('SP_API_DEFAULT_MARKETPLACE')
        self.db = db

    def fetch_products(self):
        query = "SELECT id, asin FROM products_master WHERE weight IS NULL"
        return self.db.execute_query(query)

    def fetch_product_details(self, asin):
        try:
            details = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token']).get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            return details.payload
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.fetch_product_details(asin)

    def update_product(self, product_id, weight, weight_unit, image):
        query = """
            UPDATE products_master
            SET weight = %s, weight_unit = %s, image = %s
            WHERE id = %s
        """
        params = (weight, weight_unit, image, product_id)
        self.db.execute_update(query, params)

    def process_products(self):
        products = self.fetch_products()
        for product in products:
            product_id, asin = product['id'], product['asin']
            details = self.fetch_product_details(asin)

            weight = details['attributes'].get('item_package_weight', [{'value': -1}])[0]['value']
            if weight == 0 or weight == -1:
                weight = details['attributes'].get('item_weight', [{'value': -1}])[0]['value']

            weight_unit = details['attributes'].get('item_package_weight', [{'unit': ''}])[0]['unit']
            if not weight_unit:
                weight_unit = details['attributes'].get('item_weight', [{'unit': ''}])[0]['unit']

            image = details['images'][0]['images'][0]['link'] if details['images'] else ''

            self.update_product(product_id, weight, weight_unit, image)

if __name__ == "__main__":
    db = Database()
    updater = AmazonProductUpdater(db)
    updater.process_products()
    db.close()
