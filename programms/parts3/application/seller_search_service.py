from programms.parts3.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction
from programms.parts3.domain.interface.i_api_client import IKeepaClient
from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction
from programms.parts3.domain.object.dto import SellerData, MasterData, JunctionData
from programms.parts3.domain.domain_service import DomainService

class SellerSearchService:
    def __init__(self, keepa_client: IKeepaClient, repo_seller: IRepoForSeller, repo_master: IRepoForMaster, repo_junc: IRepoForJunction) -> None:
        self.keepa_client = keepa_client
        self.repository.seller = repo_seller
        self.repository.master = repo_master
        self.repository.junction = repo_junc
        self.domain_service = DomainService()
        
    def search_seller_by_asin(self):
        dtos_master = self.domain_service.get_products_to_asin_search()
        for dto_master in dtos_master:
            sellers = self.keepa_client.query_seller_info(asin)
            # sellers の　型
            for seller in sellers:
                # saveはどうする？
                entity = ESeller(seller=seller)
                if not self.domain_service.exist(entity):
                    self.repository.save(entity)