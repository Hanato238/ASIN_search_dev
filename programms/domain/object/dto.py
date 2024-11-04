import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.object.entity import EMaster, EDetail, EEc
from typing import Dict, Any, Optional

class SellerInfoData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.seller_id = data.get('sellerId')
        self.is_fba = data.get('isFBA', False)
        self.condition = data.get('condition', None)
        self.is_shippable = data.get('isShippable', False)
        self.is_prime = data.get('isPrime', False)
        self.is_amazon = data.get('isAmazon', False)
        self.is_scam = data.get('isScam', False)
    
    def _is_competitor(self) -> int:
        # raise ValueError('Seller is Amazon')  にする？
        if self.is_amazon:
            return 1000
        elif self.is_fba and self.is_prime and self.is_shippable and self.condition == 1 and not self.is_scam:
            return 1

    def __eq__(self, other: 'SellerInfoData') -> bool:
        if not isinstance(other, SellerInfoData):
            raise ValueError('Type Error')
        if self.seller_id == other.seller_id and self.is_fba == other.is_fba and self.condition == other.condition and self.is_shippable == other.is_shippable and self.is_prime == other.is_prime and self.is_amazon == other.is_amazon and self.is_scam == other.is_scam:
            return True
        else: 
            return False
    
class MasterInfoData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.asin = data.get('asin')
        self.weight = data.get('weight', 0)
        self.weight_unit = data.get('weight_unit', None)
        self.image_url = data.get('image_url', '')

    def update_entity(self, entity: EMaster) -> EMaster:
        entity.update_asin(self.asin)
        entity.update_weight(self.weight, self.weight_unit)
        entity.update_image_url(self.image_url)
        return entity


    def __eq__(self, other: 'MasterInfoData') -> bool:
        if not isinstance(other, MasterInfoData):
            raise ValueError('Type Error')
        if self.asin == other.asin and self.weight == other.weight and self.weight_unit == other.weight_unit and self.image_url == other.image_url and self.last_search == other.last_search:
            return True
        else:
            return False

# priceとfee用に分ける？
class DetailSalesData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.asin = data.get('asin')
        self.price = data.get('price', None)
        self.currency = data.get('currency', 'JPY') 

    def update_entity(self, entity: EDetail) -> EDetail:
        entity.update_sales_price(self.price, self.currency)

class DetailCommissionData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.asin = data.get('asin')
        self.commission = data.get('fee', None)
        self.currency = data.get('currency', 'JPY') 

    def update_entity(self, entity: EDetail) -> EDetail:
        entity.update_commission(self.commission, self.currency)

# for Image Search
class EcInfoData:
    def __init__(self, ec_url: Optional[str]) -> None:
        if not isinstance(ec_url, str):
            raise ValueError('ec_url must be a string')
        self.ec_url = ec_url

    def update_entity(self, entity: EEc) -> EEc:
        entity.update_ec_url(self.ec_url)
        return entity

# for Scraper
class ScrapingInfoData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.price = data.get('price')
        self.currency = data.get('currency')
        self.is_available = data.get('isAvailable', False)

    def update_entity(self, entity: EEc) -> EEc:
        entity.update_price(self.price, self.currency)
        entity.update_is_available(self.is_available)
        return entity