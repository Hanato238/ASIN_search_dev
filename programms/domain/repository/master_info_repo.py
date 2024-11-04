import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.interface.i_repository import IRepoForMaster
from programms.domain.object.entity import EMaster
from typing import List, Optional

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