from programms.parts3.domain.interface.i_api_client import IImageSearcher
from programms.parts3.domain.interface.i_repository import IRepoForDetail, IRepoForEc
from programms.parts3.domain.object.entity import EEc
from programms.parts3.domain.domain_service import DomainService

class ImageSearchService:
    def __init__(self, image_searcher: IImageSearcher, repo_detail: IRepoForDetail, repo_ec: IRepoForEc) -> None:
        self.image_searcher = image_searcher
        self.repository.detail = repo_detail
        self.repository.ec = repo_ec
        self.domain_service = DomainService()

    def search_image(self):
        dtos = self.domain_service.get_products_to_image_search()
        image_urls = [dto.image_url for dto in dtos]
        for image_url in image_urls:
            ec_urls = self.image_searcher.search_image(image_url)
            # ec_urls の型
            for ec_url in ec_urls:
                # saveはどうする？
                entity = EEc(ec_url=ec_url)
                if not self.domain_service.exist(entity):
                    self.repository.save(entity)