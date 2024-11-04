import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.interface.i_repository import IRepoForMaster
from programms.domain.object.entity import ESeller
from typing import List, Optional

class SellerSearchRepo:
    def __init__(self, repo_master: IRepoForMaster) -> None:
        self.repo_master = repo_master

    def get_master_to_process(self) -> List[Optional[ESeller]]:
        entities_master = self.repo_master.find_by_column(is_good = True)
        return entities_master

    # command objectの導入
    def save(self, command) -> None:
        return