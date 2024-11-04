import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from programms.domain.object.dto import ScrapingInfoData
from programms.domain.interface.i_api_client import IScraper
from programms.infrastructure.client.scraper_api_client.scraper_api_client import AmazonScraper, WalmartScraper, EbayScraper

from abc import ABC, staticmethod
from typing import List, Optional

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

    def scrape(self, ec_url: str) -> List[Optional[ScrapingInfoData]]:
        scraper = self.scraper.create_scraper(ec_url)
        
        return scraper.run(ec_url)
    


