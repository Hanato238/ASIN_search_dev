from sp_api.api import CatalogItems, Products, ProductFees
from sp_api.base.exceptions import SellingApiRequestThrottledException
import time

class AmazonAPIClient:
    def __init__(self, refresh_token, lwa_app_id, lwa_client_secret, marketplace):
        self.credentials = {
            'refresh_token': refresh_token,
            'lwa_app_id': lwa_app_id,
            'lwa_client_secret': lwa_client_secret
        }
        self.marketplace = marketplace

    def request_product_details(self, result):
        try:
            asin = result['asin']
            catalog_item = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            details = catalog_item.get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            details = details.payload['attributes']
            weight = details.get('item_package_weight', [{'value': -1}])[0]['value']

            if weight == 0 or weight == -1:
                weight = details.get('item_weight', [{'value': -1}])[0]['value']
                result['weight'] = weight

            weight_unit = details.get('item_package_weight', [{'unit': ''}])[0]['unit']
            if not weight_unit:
                weight_unit = details.get('item_weight', [{'unit': ''}])[0]['unit']
                result['weight_unit'] = weight_unit

            images = details[0]['images']
            if images == []:
                image_url = ''
                print(f'No image_url found for ASIN {asin}')
            else:
                image_url = images[0]['link']
                result['image_url'] = image_url
            
            return result

        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.request_product_details(asin)

    def request_product_price(self, asin):
        try:
            products = Products(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            price = products.get_item_offers(asin, item_condition='New')
            return price.payload['Summary']['LowestPrices'][0]['ListingPrice']['Amount']
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.request_product_price(asin)
        
    def request_product_fees(self, asin, price):
        try:
            product_fees = ProductFees(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            fees = product_fees.get_product_fees_estimate_for_asin(asin, price=price, shipping=0, currency='JPY', is_fba=True)
            return fees.payload['FeesEstimateResult']['FeesEstimate']['TotalFeesEstimate']['Amount']
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.request_product_fees(asin)
        
#for test
import os
import dotenv
dotenv.load_dotenv()
def test(asin):
    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    api_client = AmazonAPIClient(**sp_credentials)
    price  = api_client.request_product_price(asin)
    fee = api_client.request_product_fees(asin, price)
    print(price)
    print(fee)

if __name__ == '__main__':
    test('B09PBPVVB6')



        
class RepositoryToGet:
    def __init__(self, db_client):
        self.db_client = db_client
    # record_products_master = {'id', 'asin', 'weight', 'weight_unit', 'image_url', 'last_search', 'is_good'}
    # record_products_detail = {'id', 'asin_id', 'ec_url_id', 'product_price', 'research_date', 'three_month_sales', 'competitors', 'sales_price', 'expected_import_fees', 'expected_roi', 'decision', 'final_dicision'} 

    # get products_master to process
    def get_product_to_process(self):
        query = "SELECT * FROM products_master WHERE weight IS NULL"
        return self.db_client.execute_quaery(query)

    # get latest product price
    def get_product_price(self, asin_id):
        query = "SELECT * FROM products_detail WHERE asin_id = %s AND commission IS NULL"
        return self.db_client.execute_query(query, (asin_id,))

class RepositoryToUpdate:
    def __init__(self, db_client):
        self.db_client = db_client

    def update_product(self, record):
        query = """
            UPDATE products_master
            SET weight = %s,
            weight_unit = %s,
            image_url = %s,
            last_search = NOW()
            WHERE id = %s;
        """
        params = (record['weight'], record['weight_unit'], record['image_url'], record['product_id'])
        return self.db_client.execute_update(query, params)

    def update_product_price(self, asin_id, product_price):
        #asin_id = record['asin_id']
        #product_price = record['product_price']
        query = "UPDATE products_detail SET product_price = %s WHERE asin_id = %s"
        return self.db_client.execute_update(query, (product_price, asin_id))
    
    def update_product_fees(self, asin, fees):
        query = "UPDATE products_detail SET commission = %s WHERE asin = %s AND commission IS NULL"
        return self.db_client.execute_update(query, (fees, asin))

class AmazonFacade:
    def __init__(self, refresh_token, lwa_app_id, lwa_client_secret, marketplace, database_client):
        self.api_client = AmazonAPIClient(refresh_token, lwa_app_id, lwa_client_secret, marketplace)
        self.get = RepositoryToGet(database_client)
        self.update = RepositoryToUpdate(database_client)

    def get_product_to_process(self):
        return self.get.get_product_to_process()

    def process_product_detail(self):
        record = self.get.get_product_to_process()
        record = self.api_client.request_product_details(record)
        return record
        self.update.update_product(record)

    def process_sales_price(self, record):
        sales_price = self.api_client.request_product_price(record['asin'])
        record['sales_price'] = sales_price
        self.update.update_product_price(record['asin_id'], sales_price)
        return record

    def process_commission(self, record):
        commission = self.api_client.request_product_fees(record['asin_id'], record['product_price'])
        record['commission'] = commission
        self.update.update_product_fees(record)
        return record
        


'''
    # compound to process_product_price_and_fees()
    def process_product_fees(self, asin):
        price = self.get.get_product_price(asin)
        fees = self.api_client.request_product_fees(asin, price)
        self.update.update_product_fees(asin, fees)
'''
def sp_api(refresh_token, lwa_app_id, lwa_client_secret, marketplace, database_client):
    return AmazonFacade(refresh_token, lwa_app_id, lwa_client_secret, marketplace, database_client)