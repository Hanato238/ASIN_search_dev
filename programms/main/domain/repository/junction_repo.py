from programms.main.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction
from programms.main.domain.object.entity import ESeller, EMaster, EJunction
from typing import Union, List, Dict

class JunctionRepo:
    def __init__(self, repo_seller: IRepoForSeller, repo_master: IRepoForMaster, repo_junction: IRepoForJunction) -> None:
        self.repo_seller = repo_seller
        self.repo_master = repo_master
        self.repo_junction = repo_junction

    def save_junction(self, entity: EJunction) -> None:
        if entity.seller_id.value is None:
            entity_seller = self.repo_seller.find_by_column(seller = entity.seller.value)
            entity.seller_id.value(entity_seller.id.value)
        if entity.product_id.value is None:
            entity_master = self.repo_master.find_by_column(asin = entity.asin.value)
            entity.product_id.value(entity_master.id.value)
        
        self.repo_junction.save(entity)