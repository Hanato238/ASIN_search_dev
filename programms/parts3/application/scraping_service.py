from programms.parts3.domain.interface.i_api_client import IScraper
from programms.parts3.domain.interface.i_repository import IRepoForEc
from programms.parts3.domain.object.entity import EEc
from programms.parts3.domain.object.dto import EcData
from programms.parts3.domain.domain_service import DomainService

class EcScrapingService:
    def __init__(self, scraper: IScraper, repo_ec: IRepoForEc) -> None:
        self.scraper = scraper
        self.repository.ec = repo_ec
        self.domain_service = DomainService()

    def scrape_ec(self, entity: EEc) -> None:
        # ec_data = {'price': Price, 'is_available': Is}
        ec_data = self.scraper.scrape_ec(entity.ec_url.value())
        entity.price = ec_data['price']
        entity.is_available = ec_data['is_available']
        return entity
        