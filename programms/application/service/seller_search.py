import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.repository.seller_search_repo import SellerSearchRepo
from programms.domain.service.seller_search_service import SellerSearchService

class SellerSearch:
    def __init__(self, service: SellerSearchService, repository: SellerSearchRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_master = self.repository.get_master_to_process()
        for entity_master in entities_master:
            data = self.service.search_seller_by_asin(entity_master.asin.value)
            for datum in data:
                for entity in datum:
                    self.repository.save(entity)
                    # junctionは?