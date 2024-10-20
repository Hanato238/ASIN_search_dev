from sp_api.api import CatalogItems, Products, ProductFees
from sp_api.base.exceptions import SellingApiRequestThrottledException

from programms.parts3.application.object.dto import MasterInfoData, DetailInfoData
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AmazonAPIClient:
    _instance = None

    def __new__(self, refresh_token: str, lwa_app_id: str, lwa_client_secret: str, marketplace: str = 'JP') -> 'AmazonAPIClient':
        if self._instance is None:
            self._instance = super().__new__(self)
            self.credentials = {
                'refresh_token': refresh_token,
                'lwa_app_id': lwa_app_id,
                'lwa_client_secret': lwa_client_secret
            }
            self.marketplace = marketplace
        return self._instance


    def request_product_details(self, asin: str) -> MasterInfoData:
        try:
            logging.info(f"Requesting product details for ASIN {asin}")
            catalog_item = CatalogItems(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            details = catalog_item.get_catalog_item(asin=asin, includedData=['attributes', 'images', 'productTypes', 'summaries'])
            attributes = details.payload['attributes']['item_package_weight'][0]
            images = details.payload['images'][0]['images']
            weight = attributes.get('value', [{'value': -1}])
            weight_unit = attributes.get('unit', [{'unit': 'None'}])
            data = {'asin': asin, 'weight': '', 'weight_unit': '', 'image_url': ''}

            if weight == 0 or weight == -1:
                data['weight'] = weight
            else: raise ValueError('weight is not found')
            if not weight_unit:
                data['weight_unit'] = weight_unit
            else: raise ValueError('weight_unit is not found')
            if images != []:
                image_url = images[0]['link']
                data['image_url'] = image_url
            else: raise ValueError('image_url is not found')

            logging.info(f"Product details for ASIN {asin} retrieved")
            return MasterInfoData(data)

        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 5 seconds before retrying...")
            time.sleep(5)
            return self.request_product_details(asin)

    def request_product_price(self, asin: str) -> DetailInfoData:
        try:
            logging.info(f"Requesting product price for ASIN {asin}")
            products = Products(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            price = products.get_item_offers(asin, item_condition='New')
            price = price.payload['Summary']['LowestPrices'][0]['ListingPrice']['Amount']
            # currencyも欲しい
            logging.info(f"Price for ASIN {asin}: {price}")
            return DetailInfoData(asin, price, currency)
        except SellingApiRequestThrottledException:
            print("Quota exceeded, waiting for 5 seconds before retrying...")
            time.sleep(5)
            return self.request_product_price(asin)
        
    def request_product_fees(self, asin: str, price: float) -> DetailInfoData:
        try:
            logging.info(f"Requesting product fees for ASIN {asin}")
            product_fees = ProductFees(credentials=self.credentials, marketplace=self.marketplace, refresh_token=self.credentials['refresh_token'])
            data = product_fees.get_product_fees_estimate_for_asin(asin, price=price, shipping=0, currency='JPY', is_fba=True)
            commission = data.payload['FeesEstimateResult']['FeesEstimate']['TotalFeesEstimate']['Amount']
            # currencyも欲しい
            logging.info(f"Fees for ASIN {asin}: {commission}")
            return DetailInfoData(asin, commission, currency)
        except SellingApiRequestThrottledException:
            logging.info("Quota exceeded, waiting for 5 seconds before retrying...")
            time.sleep(5)
            return self.request_product_fees(asin)