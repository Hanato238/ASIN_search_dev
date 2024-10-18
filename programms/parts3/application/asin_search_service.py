from programms.parts3.domain.interface.i_api_client import IKeepaClient
from programms.parts3.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction, IRepoForDetail
from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction, EDetail
from programms.parts3.infrastructure.object.dto import SellerData, MasterData, JunctionData, DetailData
from programms.parts3.domain.domain_service import DomainService
from typing import Dict

class AsinSearchService:
    def __init__(self, keepa_client: IKeepaClient, repo_seller: IRepoForSeller, repo_master: IRepoForMaster, repo_junc = IRepoForJunction, repo_detail = IRepoForDetail) -> None:
        self.keepa_client = keepa_client
        self.repository.seller = repo_seller
        self.repository.master = repo_master
        self.repository.junction = repo_junc
        self.repository.detail = repo_detail
        self.domain_service = DomainService()

    def search_asin_by_seller(self) -> None:
        dtos_seller = self.domain_service.get_products_to_seller_search()
        for dto_seller in dtos_seller:
            dtos_master = self.keepa_client.search_asin_by_seller(dto_seller.seller)
            # asinsの型
            for dto_master in dtos_master:
                # saveはどうする？
                entity = dto_master.to_entity()
                if not self.domain_service.exist(entity):
                    self.repository.save(entity)
                    self.add_junction(dto_seller, dto_master)
                    self.add_detail(dto_master)
            
    # 下記2つはdomain serviceに移動すべき？
    def add_junction(self, seller: SellerData, master: MasterData) -> None:
        if seller.id is None:
            seller.id = self.repository.seller.find_by_column(seller_id=seller.seller).id
        if master.id is None:
            master.id = self.repository.master.find_by_column(asin=master.asin).id
        dto_junction = JunctionData(EJunction(seller_id=seller.id, product_id=master.id))
        self.repository.junction.save(dto_junction)

    def add_detail(self, master: MasterData) -> None:
        if master.id is None:
            master.id = self.repository.master.find_by_column(asin=master.asin).id
        dto_detail = DetailData(EDetail(product_id=master.id))
        self.repository.detail.save(dto_detail)
