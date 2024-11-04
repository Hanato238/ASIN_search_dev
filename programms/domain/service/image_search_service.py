import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.interface.i_api_client import IImageSearcher
from programms.domain.object.entity import EMaster, EEc

from typing import List, Optional

class ImageSearchService:
    def __init__(self, image_searcher: IImageSearcher) -> None:
        self.image_searcher = image_searcher

    def search_image(self, entity_master: EMaster) -> List[Optional[EEc]]:
        entities_ec = []
        ec_infos = self.image_searcher.search_image(entity_master.image_url.value)
        for ec_info in ec_infos:
            entity_ec = ec_info.update_entity(EEc(product_id=entity_master.id.value))
            entities_ec.append(entity_ec)
        return entities_ec