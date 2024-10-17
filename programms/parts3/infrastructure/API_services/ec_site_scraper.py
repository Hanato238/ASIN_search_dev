from programms.parts3.domain.interface.i_api_client import IScraper
from programms.parts3.infrastructure.api_services.scraper_api_client.scraper_api_client import AmazonScraper, WalmartScraper, EbayScraper
from programms.parts3.domain.interface.i_repository import IRepoForEc
from programms.parts3.domain.object.entity import EEc
from programms.parts3.domain.object.dto import EcData
from abc import ABC, abstractmethod

class ScraperFactory(ABC):
    @staticmethod
    def create_scraper() -> IScraper:
        if A:
            return AmazonScraper()
        elif B:
            return WalmartScraper()
        elif C:
            return EbayScraper()
        
class EcScrapingService:
    def __init__(self, scraper: ScraperFactory, repo_ec: IRepoForEc) -> None:
        self.scraper = scraper
        self.repository.ec = repo_ec

    def scrape(self, entity: EEc) -> None:
        scraper = self.scraper.create_scraper(entity.ec_url.value)
        
        return self.scraper.create_scraper(entity.ec_url.value).run(entity.ec_url.value())
    


