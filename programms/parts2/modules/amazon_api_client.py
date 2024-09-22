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

    def fetch_product_details(self, asin):
        try:
            catalog_item = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            details = catalog_item.get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            return details.payload
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.fetch_product_details(asin)

    def get_product_price(self, asin):
        try:
            products = Products(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            price = products.get_item_offers(asin, item_condition='New')
            return price.payload['Summary']['LowestPrices'][0]['ListingPrice']['Amount']
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.get_product_price(asin)
        
    def get_product_fees(self, asin, price):
        try:
            product_fees = ProductFees(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            fees = product_fees.get_product_fees_estimate_for_asin(asin, price=price, shipping=0, currency='JPY', is_fba=True)
            return fees.payload['FeesEstimateResult']['FeesEstimate']['TotalFeesEstimate']['Amount']
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.get_product_fees(asin)
        
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
    price  = api_client.get_product_price(asin)
    fee = api_client.get_product_fees(asin, price)
    print(price)
    print(fee)

if __name__ == '__main__':
    test('B09PBPVVB6')



class RepositoryForSpAPI:
    def __init__(self, db_client):
        self.db_client = db_client
    
    def fetch_products(self):
        query = "SELECT id, asin FROM products_master WHERE weight IS NULL"
        return self.db_client.execute_quaery(query)

    def get_product_price(self, asin):
        query = "SELECT product_price FROM products_detail WHERE asin = %s AND commission IS NULL"
        return self.db_client.execute_query(query, (asin,))

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
    
    def update_product_price(self, asin, price):
        query = "UPDATE products_detail SET product_price = %s WHERE asin = %s"
        return self.db_client.execute_update(query, (price, asin))
    
    def update_product_fees(self, asin, fees):
        query = "UPDATE products_detail SET commission = %s WHERE asin = %s AND commission IS NULL"
        return self.db_client.execute_update(query, (fees, asin))

class AmazonFacade:
    def __init__(self, refresh_token, lwa_app_id, lwa_client_secret, marketplace, database_client):
        self.api_client = AmazonAPIClient(refresh_token, lwa_app_id, lwa_client_secret, marketplace)
        self.repository = RepositoryForSpAPI(database_client)

    def update_product_details(self, product):
        product_details = self.api_client.fetch_product_details(product)
        self.api_client.product_details_updater(product_details)

    # update products_detail set product_price = price where asin = asin
    def update_procuct_price(self, asin, price):
        lowest_price = self.api_client.update_product_price(asin, price)
        self.repository.update_product_price(asin, lowest_price)
        fees = self.api_client.get_product_fees(asin, lowest_price)
        self.repository.update_product_fees(asin, fees)

    # get product_detail through API and update products_master
    def fetch_product_details(self, product):
        product_id, asin = product['id'], product['asin']
        details = self.api_client.fetch_product_details(asin)

        weight = details['attributes'].get('item_package_weight', [{'value': -1}])[0]['value']
        if weight == 0 or weight == -1:
            weight = details['attributes'].get('item_weight', [{'value': -1}])[0]['value']

        weight_unit = details['attributes'].get('item_package_weight', [{'unit': ''}])[0]['unit']
        if not weight_unit:
            weight_unit = details['attributes'].get('item_weight', [{'unit': ''}])[0]['unit']

        images = details['images'][0]['images']
        if images == []:
            image_url = ''
            print(f'No image_url found for ASIN {asin}')
        else:
            image_url = images[0]['link']

        print(f'ASIN {asin} weights {weight}{weight_unit}')
        details = {'id':product_id, 'asin':asin, 'weight':weight, 'weight_unit':weight_unit, 'image_url':image_url}
        self.product_details_updater(details)
        return details
    # called by fetch_product_details
    def product_details_updater(self, product_details):
        self.repository.update_product(
            product_details['id'],
            product_details['weight'],
            product_details['weight_unit'],
            product_details['image_url']
        )

    def update_product_fee(self, asin):
        price = self.repository.get_product_price(asin)
        fees = self.api_client.get_product_fees(asin, price)
        self.repository.update_product_fees(asin, fees)

def sp_api(refresh_token, lwa_app_id, lwa_client_secret, marketplace, database_client):
    return AmazonFacade(refresh_token, lwa_app_id, lwa_client_secret, marketplace, database_client)