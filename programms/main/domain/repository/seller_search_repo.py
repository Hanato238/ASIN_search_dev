from programms.main.domain.interface.i_repository import IRepoForMaster
from programms.main.domain.object.entity import ESeller
from typing import Union, List, Dict, Optional

class SellerSearchRepo:
    def __init__(self, repo_master: IRepoForMaster) -> None:
        self.repo_master = repo_master

    def get_master_to_process(self) -> List[Optional[ESeller]]:
        entities_master = self.repo_master.find_by_column(is_good = True)
        return entities_master

    # command objectの導入
    def save(self, command) -> None:
        return