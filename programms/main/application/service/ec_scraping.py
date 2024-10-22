from programms.main.domain.repository.ec_scraping_repo import EcScrapingRepo
from programms.main.domain.service.ec_scraping_service import EcScrapingService

class EcScraping:
    def __init__(self, service: EcScrapingService, repository: EcScrapingRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_master = self.repository.get_master_to_process()
        for entity_master in entities_master:
            entities_ec = self.service.search_ec(entity_master.asin.value)
            for entity_ec in entities_ec:
                self.repository.save(entity_ec)