from programms.parts3.domain.interface.i_api_client import IScraper
from programms.parts3.infrastructure.api_services.scraper_api_client.scraper_api_client import AmazonScraper, WalmartScraper, EbayScraper
from programms.parts3.infrastructure.object.dto import EcData
from abc import ABC, staticmethod

class ScraperFactory(ABC):
    @staticmethod
    def create_scraper(url) -> IScraper:
        if url == 'amazon':
            return AmazonScraper()
        elif url == 'walmart':
            return WalmartScraper()
        elif url == 'ebay':
            return EbayScraper()
        
class EcScrapingService:
    def __init__(self, scraper: ScraperFactory) -> None:
        self.scraper = scraper

    def scrape(self, dto: EcData) -> None:
        scraper = self.scraper.create_scraper(dto.ec_url)
        
        return scraper.run(dto.ec_url)
    


