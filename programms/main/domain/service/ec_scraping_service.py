from programms.main.domain.interface.i_api_client import IScraper
from programms.main.domain.object.entity import EEc

from typing import List, Optional

class EcScrapingService:
    def __init__(self, scraper: IScraper) -> None:
        self.scraper = scraper

    def scrape_ec(self, entity_ec: EEc) -> List[Optional[EEc]]:
        # ec_data: Dict[str, Any]
        ec_data = self.scraper.scrape_ec(entity_ec.ec_url.value)
        entities_ec = []
        for ec_datum in ec_data:
            new_entity_ec = entity_ec.update_entity(ec_datum)
            entities_ec.append(new_entity_ec)
        return entities_ec