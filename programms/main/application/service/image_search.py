from programms.main.domain.repository.master_info_repo import MasterInfoRepo
from programms.main.domain.service.image_search_service import ImageSearchService

class ImageSearch:
    def __init__(self, service: ImageSearchService, repository: MasterInfoRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_master = self.repository.get_master_to_image_search()
        for entity_master in entities_master:
            entities_ec = self.service.search_image(entity_master.image_url.value)
            for entity_ec in entities_ec:
                self.repository.save(entity_ec)