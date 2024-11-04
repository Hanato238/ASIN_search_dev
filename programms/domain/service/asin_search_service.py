import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.interface.i_api_client import IKeepaClient
from programms.domain.object.entity import ESeller, EMaster, EJunction, EDetail

from typing import List, Tuple, Optional

class AsinSearchService:
    def __init__(self, keepa_client: IKeepaClient) -> None:
        self.keepa_client = keepa_client

    def search_asin_by_seller(self, entity_seller: ESeller) -> Optional[List[Tuple[(EMaster, EJunction, EDetail)]]]:
        data = []
        asins = self.keepa_client.search_asin_by_seller(entity_seller.seller.value)
        # asinsの型
        for asin in asins:
            entity_master = EMaster(asin=asin)
            entity_junction = EJunction(seller_id=entity_seller.id.value, seller=entity_seller.seller.value, asin=asin)
            entity_detail = EDetail(asin=asin)
            datum = (entity_master, entity_junction, entity_detail)
            data.append(datum)
        return data