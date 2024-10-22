from programms.main.domain.object.entity import EEc
from programms.main.domain.object.dto import SellerData
from typing import Union, List, Dict, Optional
import logging

class DomainService:
    def __init__(self) -> None:
        pass

    def compare_prices(self, entities_ec: List[EEc]) -> Dict[int, float]:
        min_price = float('inf')
        min_price_product = {'ec_id': None, 'price': None}
        for entity_ec in entities_ec:
            price = entity_ec.price.convert_to_jpy()
            if price < min_price:
                min_price = price
                min_price_product = {'ec_id': entity_ec.id.value, 'price': price}
        return min_price_product
    
    def count_competitors(self, data: SellerData) -> Optional[int]:
        competitors = 0
        for datum in data:
            if datum._is_competitor():
                competitors += 1
        return competitors
