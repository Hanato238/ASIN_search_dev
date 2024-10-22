from programms.main.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from typing import Dict, Any, Optional

class SellerInfoData:
    def __init__(self, data: Dict[Any]) -> None:
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
        elif self.is_prime:
            return 1

class MasterInfoData:
    def __init__(self, data: Dict[Any]) -> None:
        self.asin = data.get('asin')
        self.weight = data.get('weight', 0)
        self.weight_unit = data.get('weightUnit', None)
        self.image_url = data.get('imageUrl', '')
        self.last_search = data.get('lastSearch')
        self.is_good = data.get('isGood', False)
    
    def update_entity(self, entity: EMaster) -> EMaster:
        entity.weight(self.weight, self.weight_unit)
        entity.image_url(self.image_url)
        entity.last_search(self.last_search)
        entity.is_good(self.is_good)

class DetailInfoData:
    def __init__(self, data: Dict[Any]) -> None:
        self.asin = data.get('asin')
        self.price = data.get('price', None)
        self.currency = data.get('currency', 'JPY') 

    def update_entity(self, entity: EDetail) -> EDetail:
        entity.sales_price(self.price, self.currency)


# for Image Search
class EcInfoData:
    def __init__(self, ec_url: Optional[str]) -> None:
        self.ec_url = ec_url

    def update_entity(self, entity: EEc) -> EEc:
        entity.ec_url(self.ec_url)

# for Scraper
class ScrapingInfoData:
    def __init__(self, data: Dict[Any]) -> None:
        self.price = data.get('price')
        self.currency = data.get('currency')
        self.is_available = data.get('isAvailable', False)

    def update_entity(self, entity: EEc) -> EEc:
        entity.price(self.price, self.currency)
        entity.is_available(self.is_available)