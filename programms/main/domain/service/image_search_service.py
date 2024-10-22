from programms.main.domain.interface.i_api_client import IImageSearcher
from programms.main.domain.object.entity import EMaster, EEc

from typing import List, Optional

class ImageSearchService:
    def __init__(self, image_searcher: IImageSearcher) -> None:
        self.image_searcher = image_searcher

    def search_image(self, entity_master: EMaster) -> List[EEc]:
        entities_ec = []
        ec_urls = self.image_searcher.search_image(entity_master.image_url.value)
        for ec_url in ec_urls:
            entity_ec = EEc(product_id=entity_master.id.value, ec_url=ec_url)
            entities_ec.append(entity_ec)
        return entities_ec