from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.parts3.domain.object.value import Id, Is, SellerId, Asin, Weight, ImageURL, EcURL, LastSearch, Price
from typing import Dict, Any, Optional

# filed変数はすべて_が必要？

## for Entities
class SellerData:
    def __init__(self, seller: ESeller) -> Dict[str, Any]:
        self.id = seller.id.value()
        self.seller = seller.seller.value()
        self.is_good = seller.is_good.value()

    def __repr__(self) -> str:
        return f"SellerData(id={self.id}, seller={self.seller}, is_good={self.is_good})"

    def _to_entity(self) -> ESeller:
        entity = ESeller(self.id, self.seller, self.is_good)
        return entity

class MasterData:
    def __init__(self, master: EMaster) -> Dict[str, Any]:
        self.id = master.id.value()
        self.asin = master.asin.value()
        self.weight = master.weight.value()
        self.unit = master.weight.unit()
        self.image_url = master.image_url.value()
        self.last_search = master.last_search.value()
        self.ec_search = master.ec_search.value()
        self.is_good = master.is_good.value()
        self.is_filled = master.is_filled.value()

    def __repr__(self) -> str:
        return f"MasterData(id={self.id}, asin={self.asin}, weight={self.weight}, "

    def _to_entity(self) -> EMaster:
        entity = EMaster(self.id, self.asin, self.weight, self.unit, self.image_url, self.last_search, self.ec_search, self.is_good, self.is_filled)
        return entity

class JunctionData:
    def __init__(self, junction: EJunction, seller: ESeller, master:EMaster) -> Dict[str, Any]:
        self.id = junction.id.value()
        self.seller_id = junction.seller_id.value()
        self.product_id = junction.product_id.value()

        self.seller = seller.seller.value()
        self.asin = master.asin.value()

    def __repr__(self) -> str:
        return f"JunctionData(id={self.id}, seller_id={self.seller_id}, product_id={self.product_id})"

    def _to_entity(self) -> EJunction:
        entity = EJunction(self.id, self.seller_id, self.product_id)
        return entity

class DetailData:
    def __init__(self, detail: EDetail, master: EMaster = None) -> Dict[str, Any]:
        self.id = detail.id.value()
        self.product_id = detail.product_id.value()

        self.asin = master.asin.value()
        self.weight = master.weight.value()
        self.unit = master.weight.unit()
        self.last_search = master.last_search.value()

        self.ec_id = detail.ec_id.value()
        self.purchase_price = detail.purchase_price.value()
        self.research_date = detail.research_date.value()
        self.three_month_sales = detail.three_month_sales.value()
        self.competitors = detail.competitors.value()
        self.sales_price = detail.sales_price.value()
        self.commission = detail.commission.value()
        self.import_fees = detail.import_fees.value()
        self.roi = detail.roi
        self.decision = detail.decision.value()
        self.final_decision = detail.final_decision.value()
        self.is_filled = detail.is_filled.value()
    
    def __repr__(self) -> str:
        return (f"DetailData(id={self.id}, product_id={self.product_id}, weight={self.weight}, "
                f"unit={self.unit}, last_search={self.last_search}, ec_id={self.ec_id}, "
                f"purchase_price={self.purchase_price}, research_date={self.research_date}, "
                f"three_month_sales={self.three_month_sales}, competitors={self.competitors}, "
                f"sales_price={self.sales_price}, commission={self.commission}, import_fees={self.import_fees}, "
                f"roi={self.roi}, decision={self.decision}, final_decision={self.final_decision}, "
                f"is_filled={self.is_filled})")

    def _to_entity(self) -> None:
        entity = EDetail(self.id, self.product_id, self.asin, self.weight, self.weight_unit, self.last_search, self.ec_id, self.purchase_price, self.research_date, self.three_month_sales, self.competitors, self.sales_price, self.commission, self.import_fees, self.roi, self.decision, self.final_decision, self.is_filled)
        return entity

# masterと連結？
class EcData:
    def __init__(self, ec: EEc, master: EMaster = None) -> Dict[str, Any]:
        self.id = ec.id.value()
        self.product_id = ec.product_id.value()

        self.asin = master.asin.value()
        self.image_url = master.image_url.value()

        self.price = ec.price.value()
        self.currency = self.price.currency()
        self.is_available = ec.is_available.value()
        self.ec_url = ec.ec_url.value()
        self.is_filled = ec.is_filled.value()
        self.is_supported = ec.is_supported.value()

    def __repr__(self) -> str:
        return (f"EcData(id={self.id}, product_id={self.product_id}, price={self.price}, "
                f"currency={self.currency}, is_available={self.is_available}, ec_url={self.ec_url}, "
                f"is_filled={self.is_filled}, is_supported={self.is_supported})")

    def _to_entity(self) -> None:
        entity = EEc(self.id, self.product_id, self.asin, self.image_url, self.price, self.currency, self.is_available, self.ec_url, self.is_filled, self.is_supported)
        return entity
    

# for Keepa
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

        
## ここから下、dataの型ヒントを調整.必ずしもdictがfullであるわけではない
# for AmazonAPI
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