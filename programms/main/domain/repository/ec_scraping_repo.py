from programms.main.domain.interface.i_repository import IRepoForEc
from programms.main.domain.object.entity import EEc

from typing import Union, List, Dict, Optional

class EcScrapingRepo:
    def __init__(self, repo_ec: IRepoForEc) -> None:
        self.repo_ec = repo_ec

    def get_ec_to_process(self) -> List[Optional[EEc]]:
        entities_ec = self.repo_ec.find_by_column(is_scraped = False)
        return entities_ec
    
    # command objectの導入
    def save(self, command) -> None:
        return

    def get_ec_sales(self, product_id: int) -> List[Optional[EEc]]:
        entities_ec = self.repo_ec.find_by_column(product_id=product_id)
        return entities_ec