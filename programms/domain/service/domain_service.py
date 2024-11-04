import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.object.entity import EDetail, EEc
from programms.domain.object.dto import SellerInfoData
from programms.infrastructure.repository.repository import RepoForEc
from typing import List, Dict, Optional
import logging

class DomainService:
    def __init__(self) -> None:
        pass

    def compare_prices(self, entity_detail: EDetail) -> Dict[int, float]:
        entities_ec = self.repository.ec.find_by_column(product_id=entity_detail.product_id.value)
        min_price = float('inf')
        min_price_product = {'ec_id': None, 'price': None}
        for entity_ec in entities_ec:
            price = entity_ec.price.convert_to_jpy()
            if price < min_price:
                min_price = price
                min_price_product = {'ec_id': entity_ec.id.value, 'price': price}
        return min_price_product
    
    def count_competitors(self, data: SellerInfoData) -> Optional[int]:
        competitors = 0
        for datum in data:
            if datum._is_competitor():
                competitors += 1
        return competitors
