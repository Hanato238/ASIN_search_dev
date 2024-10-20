from programms.parts3.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction, IRepoForDetail, IRepoForEc
from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.parts3.domain.service.user_service import UserService
from programms.parts3.application.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData

from typing import List, Optional


class AsinSearchRepo:
    def __init__(self, repo_seller: IRepoForSeller) -> None:
        self.repo_seller = repo_seller

    def get_master_to_process(self) -> List[Optional[EMaster]]:
        entities_seller = self.repo_seller.find_by_column(is_good = True)
        return entities_seller
    
    def get_master_to_evaluate(self) -> List[Optional[EMaster]]:
        entities_seller = self.repo_seller.find_by_column(is_good = False)
        return entities_seller
    
    # command objectの導入
    def save(self, command) -> None:
        return

class SellerSearchRepo:
    def __init__(self, repo_master: IRepoForMaster) -> None:
        self.repo_master = repo_master

    def get_seller_to_process(self) -> List[Optional[ESeller]]:
        entities_master = self.repo_master.find_by_column(is_good = True)
        return entities_master

    # command objectの導入
    def save(self, command) -> None:
        return
    
class MasterInfoRepo:
    def __init__(self, repo_master: IRepoForMaster) -> None:
        self.repo_master = repo_master

    def get_master_to_process(self) -> List[Optional[EMaster]]:
        entities_master = self.repo_master.find_by_column(is_filled = False)
        return entities_master
    
    def get_master_to_image_search(self) -> List[Optional[EMaster]]:
        entities_master = self.repo_master.find_by_column(is_filled = True, ec_search = False)
        return entities_master
    
    # command objectの導入
    def save(self, command) -> None:
        return

class EcScrapingRepo:
    def __init__(self, repo_ec: IRepoForEc) -> None:
        self.repo_ec = repo_ec

    def get_ec_to_process(self) -> List[Optional[EEc]]:
        entities_ec = self.repo_ec.find_by_column(is_scraped = False)
        return entities_ec
    
    # command objectの導入
    def save(self, command) -> None:
        return
    
class DetailInfoRepo:
    def __init__(self, repo_master: IRepoForMaster, repo_detail: IRepoForDetail) -> None:
        self.repo_master = repo_master
        self.repo_detail = repo_detail
    
    def get_detail_to_process(self) -> List[Optional[EDetail]]:
        entities_detail = self.repo_detail.find_by_column(is_filled = False)
        return entities_detail
    
    # command objectの導入
    def save(self, command) -> None:
        return
    


## ???
class ApiClientRepo:
    def __init__(self, repo_for_seller: IRepoForSeller, repo_for_master: IRepoForMaster, repo_for_junction: IRepoForJunction, repo_for_detail: IRepoForDetail, repo_for_ec: IRepoForEc) -> None:
        self.repo_for_seller = repo_for_seller
        self.repo_for_master = repo_for_master
        self.repo_for_junction = repo_for_junction
        self.repo_for_detail = repo_for_detail
        self.repo_for_ec = repo_for_ec

    def search_products_by_seller(self, seller:SellerData) -> List[MasterData]:
        data_asins = self.keepa_client.search_asin_by_seller(seller.seller.value)
        dtos = []
        for data_asin in data_asins:
            dto = MasterData(asin = data_asin)
            dtos.append(dto)
        return dtos
    
    def search_sellers_by_product(self, master: MasterData) -> List[SellerData]:
        data_sellers = self.keepa_client.query_seller_info(master.asin.value)
        dtos = []
        for datum in data_sellers:
            dto = SellerData(seller = datum['seller'])
            dtos.append(dto)
        return dtos
    
    def search_competitors_by_seller(self, master: MasterData) -> int:
        data_sellers = self.keepa_client.query_seller_info(master.asin.value)
        competitors = 0
        for datum in data_sellers:
            if datum._is_competitor():
                competitors += 1
        return competitors

    def search_three_month_sales(self, asin:str) -> List[EMaster]:
        data_sales = self.keepa_client.get_sales_rank_drops(asin)
        dtos = []
        for data_sale in data_sales:
            dto = MasterData(three_month_sales = data_sale)
            dtos.append(dto)
        return dtos