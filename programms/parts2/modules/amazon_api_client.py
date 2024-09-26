from sp_api.api import CatalogItems, Products, ProductFees
from sp_api.base.exceptions import SellingApiRequestThrottledException
import time
import time
import logging
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AmazonAPIClient:
    def __init__(self, refresh_token: str, lwa_app_id: str, lwa_client_secret: str, marketplace: str) -> None:
        self.credentials = {
            'refresh_token': refresh_token,
            'lwa_app_id': lwa_app_id,
            'lwa_client_secret': lwa_client_secret
        }
        self.marketplace = marketplace

    def request_product_details(self, result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            asin = result['asin']
            logging.info(f"Requesting product details for ASIN {asin}")
            catalog_item = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            details = catalog_item.get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            attributes = details.payload['attributes']['item_package_weight'][0]
            images = details.payload['images']

            weight = attributes.get('value', [{'value': -1}])
            weight_unit = attributes.get('unit', [{'unit': 'None'}])

            if weight == 0 or weight == -1:
                result['weight'] = weight

            if not weight_unit:
                result['weight_unit'] = weight_unit

            images = images[0]['images']
            if images == []:
                image_url = ''
                logger.info(f"No image found for ASIN {asin}")
            else:
                image_url = images[0]['link']
                result['image_url'] = image_url
            
            logging.info(f"Product details for ASIN {asin} retrieved")
            return result

        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.request_product_details(asin)

    def request_product_price(self, asin: str) -> float:
        try:
            logging.info(f"Requesting product price for ASIN {asin}")
            products = Products(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            price = products.get_item_offers(asin, item_condition='New')
            price = price.payload['Summary']['LowestPrices'][0]['ListingPrice']['Amount']
            logging.info(f"Price for ASIN {asin}: {price}")
            return price
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.request_product_price(asin)
        
    def request_product_fees(self, asin: str, price: float) -> float:
        try:
            logging.info(f"Requesting product fees for ASIN {asin}")
            product_fees = ProductFees(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            fees = product_fees.get_product_fees_estimate_for_asin(asin, price=price, shipping=0, currency='JPY', is_fba=True)
            fees = fees.payload['FeesEstimateResult']['FeesEstimate']['TotalFeesEstimate']['Amount']
            logging.info(f"Fees for ASIN {asin}: {fees}")
            return fees
        except SellingApiRequestThrottledException:
            logging.info("Quota exceeded, waiting for 60 seconds before retrying...")
            time.sleep(60)
            return self.request_product_fees(asin)
        
class RepositoryToGet:
    def __init__(self, db_client: Any)  -> None:
        self.db_client = db_client
    # record_products_master = {'id', 'asin', 'weight', 'weight_unit', 'image_url', 'last_search', 'is_good'}
    # record_products_detail = {'id', 'asin_id', 'ec_url_id', 'product_price', 'research_date', 'three_month_sales', 'competitors', 'sales_price', 'expected_import_fees', 'expected_roi', 'decision', 'final_dicision'} 

    # get products_master to process
    def get_product_to_process(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_master WHERE weight IS NULL"
        result = self.db_client.execute_query(query)
        logging.info(f"Found {len(result)} products to process")
        return result

    # get latest product price
    def get_product_price(self, asin_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_detail WHERE asin_id = %s AND commission IS NULL"
        result = self.db_client.execute_query(query, (asin_id,))
        logging.info(f"Price for asin_id {asin_id}: {result['product_price']}")
        return result
    
    def get_asin_from_product_detail(self, product_id: int) -> str:
        # JOINいらんくね？
        query = """
            SELECT asin FROM products_master WHERE id = %s;
            """
        #query = "SELECT asin_id FROM products_detail WHERE id = %s"
        result = self.db_client.execute_query(query, (product_id,))[0]
        logging.info(f"ASIN for product_id {product_id}: {result}")
        return result
class RepositoryToUpdate:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def update_product(self, record: Dict[str, Any]) -> None:
        query = """
            UPDATE products_master
            SET weight = %s,
            weight_unit = %s,
            image_url = %s,
            last_search = NOW()
            WHERE id = %s;
        """
        params = (record['weight'], record['weight_unit'], record['image_url'], record['id'])
        self.db_client.execute_update(query, params)
        logging.info(f"Update product: {record['id']}")

    def update_product_price(self, asin_id: int, product_price: float) -> None:
        #asin_id = record['asin_id']
        #product_price = record['product_price']
        query = "UPDATE products_detail SET product_price = %s WHERE asin_id = %s"
        self.db_client.execute_update(query, (product_price, asin_id))
        logging.info(f"Updated product price for asin_id {asin_id}")
    
    def update_product_fees(self, asin_id: int, fees: float) -> None:
        query = "UPDATE products_detail SET commission = %s WHERE asin_id = %s AND commission IS NULL"
        self.db_client.execute_update(query, (fees, asin_id))
        logging.info(f"Updated product fees for asin_id {asin_id}")

class AmazonFacade:
    def __init__(self, refresh_token: str, lwa_app_id: str, lwa_client_secret: str, marketplace: str, database_client: Any) -> None:
        self.api_client = AmazonAPIClient(refresh_token, lwa_app_id, lwa_client_secret, marketplace)
        self.get = RepositoryToGet(database_client)
        self.update = RepositoryToUpdate(database_client)

    def get_product_to_process(self) -> List[Dict[str, Any]]:
        return self.get.get_product_to_process()

    def process_product_detail(self, record_product_master: Dict[str, Any]) -> Dict[str, Any]:
        record_product_master = self.api_client.request_product_details(record_product_master)
        self.update.update_product(record_product_master)
        return record_product_master

    def process_sales_price(self, record: Dict[str, Any]) -> Dict[str, Any]:
        asin = self.get.get_asin_from_product_detail(record['asin_id'])
        sales_price = self.api_client.request_product_price(asin)
        record['sales_price'] = sales_price
        self.update.update_product_price(record['asin_id'], sales_price)
        return record

    def process_commission(self, record: Dict[str, Any]) -> Dict[str, Any]:
        asin = self.get.get_asin_from_product_detail(record['asin_id'])
        commission = self.api_client.request_product_fees(asin, record['sales_price'])
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
def sp_api(refresh_token: str, lwa_app_id: str, lwa_client_secret: str, marketplace: str, database_client: Any) -> AmazonFacade:
    return AmazonFacade(refresh_token, lwa_app_id, lwa_client_secret, marketplace, database_client)