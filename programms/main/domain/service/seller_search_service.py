from programms.main.domain.interface.i_api_client import IKeepaClient
from programms.main.domain.object.entity import ESeller, EMaster, EJunction

from typing import List, Optional

class SellerSearchService:
    def __init__(self, keepa_client: IKeepaClient) -> None:
        self.keepa_client = keepa_client
        
    def search_seller_by_asin(self, entity_master: EMaster) -> List[(ESeller, EJunction)]:
        data = []
        sellers = self.keepa_client.query_seller_info(entity_master.asin.value)
        # sellers: List[str]
        for seller in sellers:
            entity_seller = ESeller(seller=seller)
            # error("seller_id=None")
            entity_junction = EJunction(seller_id=entity_seller.id.value, product_id=entity_master.id.value, seller=entity_seller.seller.value, asin=entity_master.asin.value)
            datum = (entity_seller, entity_junction)
            data.append(datum)
        return data