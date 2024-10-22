from programms.main.domain.interface.i_repository import IRepoForMaster,  IRepoForDetail
from programms.main.domain.object.entity import EDetail
from typing import Union, List, Dict, Optional

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