import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.interface.i_api_client import IScraper
from programms.domain.object.entity import EEc

from typing import List, Optional

class EcScrapingService:
    def __init__(self, scraper: IScraper) -> None:
        self.scraper = scraper

    def scrape_ec(self, entity_ec: EEc) -> List[Optional[EEc]]:
        # ec_data: Dict[str, Any]
        ec_infos = self.scraper.scrape_ec(entity_ec.ec_url.value)
        entities_ec = []
        for ec_info in ec_infos:
            new_entity_ec = ec_info.update_entity(entity_ec)
            entities_ec.append(new_entity_ec)
        return entities_ec