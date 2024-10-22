from programms.main.domain.interface.i_api_client import IAmazonAPIClient, IImageSearcher
from programms.main.domain.object.entity import EMaster, EEc

from typing import List, Optional

class MasterInfoService:
    def __init__(self, amazon_api_client: IAmazonAPIClient) -> None:
        self.amazon_api_client = amazon_api_client

    def get_master_info(self, entity_master: EMaster) -> EMaster:
        data = self.amazon_api_client.request_product_details(entity_master.asin.value)
        new_entity_master = data.update_entity(entity_master)
        return new_entity_master
    

###　どうする？
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
    