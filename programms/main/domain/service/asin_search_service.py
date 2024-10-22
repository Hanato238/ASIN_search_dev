from programms.main.domain.interface.i_api_client import IKeepaClient
from programms.main.domain.object.entity import ESeller, EMaster, EJunction, EDetail

from typing import List, Optional

class AsinSearchService:
    def __init__(self, keepa_client: IKeepaClient) -> None:
        self.keepa_client = keepa_client

    def search_asin_by_seller(self, entity_seller: ESeller) -> List[(EMaster, EJunction, EDetail)]:
        data = []
        entities_master = self.keepa_client.search_asin_by_seller(entity_seller.seller.value)
        # asinsの型
        for entity_master in entities_master:
            entity_junction = EJunction(seller_id=entity_seller.id.value, product_id=entity_master.id.value, seller=entity_seller.seller.value, asin=entity_master.asin.value)
            entity_detail = EDetail(id=entity_master.id.value, asin=entity_master.asin.value)
            datum = (entity_master, entity_junction, entity_detail)
            data.append(datum)
        return data