import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from programms.domain.repository.asin_search_repo import AsinSearchRepo
from programms.domain.service.asin_search_service import AsinSearchService

class AsinSearch:
    def __init__(self, service: AsinSearchService, repository: AsinSearchRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_seller = self.repository.get_seller_to_process()
        for entity_seller in entities_seller:
            data = self.service.search_asin_by_seller(entity_seller.seller.value)
            for datum in data:
                for entity in datum:
                    self.repository.save(entity)
                    # junctionは?