import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.interface.i_repository import IRepoForSeller
from programms.domain.object.entity import EMaster
from typing import List, Optional

class AsinSearchRepo:
    def __init__(self, repo_seller: IRepoForSeller) -> None:
        self.repo_seller = repo_seller

    def get_seller_to_process(self) -> List[Optional[EMaster]]:
        entities_seller = self.repo_seller.find_by_column(is_good = True)
        return entities_seller
    
    def get_master_to_evaluate(self) -> List[Optional[EMaster]]:
        entities_seller = self.repo_seller.find_by_column(is_good = False)
        return entities_seller
    
    # command objectの導入
    def save(self, command) -> None:
        return