import time
import dotenv
import os
from sp_api.api import CatalogItems
import mysql.connector
from sp_api.base.exceptions import SellingApiRequestThrottledException

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
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

class RepositoryForSpAPI:
    def __init__(self, db_client):
        self.db_client = db_client
    
    def fetch_products(self):
        query = "SELECT id, asin FROM products_master WHERE weight IS NULL"
        return self.db_client.execute_query(query)

    def update_product(self, product_id, weight, weight_unit, image_url):
        query = """
            UPDATE products_master
            SET weight = %s,
            weight_unit = %s,
            image_url = %s,
            last_search = NOW()
            WHERE id = %s;
        """
        params = (weight, weight_unit, image_url, product_id)
        return self.db_client.execute_update(query, params)
    
class AmazonAPIClient:
    def __init__(self, refresh_token, lwa_app_id, lwa_client_secret, marketplace):
        self.credentials = {
            'refresh_token': refresh_token,
            'lwa_app_id': lwa_app_id,
            'lwa_client_secret': lwa_client_secret
        }
        self.marketplace = marketplace

    def fetch_product_details(self, asin):
        try:
            details = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token']).get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            return details.payload
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.fetch_product_details(asin)

class AmazonProductUpdater:
    def __init__(self, db_client, api_client):
        self.db_client = db_client
        self.api = api_client

    def process_products(self):
        products = self.db_client.fetch_products()
        for product in products:
            product_id, asin = product['id'], product['asin']
            details = self.api.fetch_product_details(asin)

            weight = details['attributes'].get('item_package_weight', [{'value': -1}])[0]['value']
            if weight == 0 or weight == -1:
                weight = details['attributes'].get('item_weight', [{'value': -1}])[0]['value']

            weight_unit = details['attributes'].get('item_package_weight', [{'unit': ''}])[0]['unit']
            if not weight_unit:
                weight_unit = details['attributes'].get('item_weight', [{'unit': ''}])[0]['unit']

            image_url = details['images'][0]['images'][0]['link'] if details['images'] else ''

            self.db_client.update_product(product_id, weight, weight_unit, image_url)

def main():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = DatabaseClient(**db_config)
    repository = RepositoryForSpAPI(db_client)
    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    api_client = AmazonAPIClient(**sp_credentials)
    updater = AmazonProductUpdater(repository, api_client)
    updater.process_products()
    db_client.close()

if __name__ == "__main__":
    main()
