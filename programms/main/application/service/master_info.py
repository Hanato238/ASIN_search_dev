from programms.main.domain.repository.master_info_repo import MasterInfoRepo
from programms.main.domain.service.master_info_service import MasterInfoService

class MasterInfo:
    def __init__(self, service: MasterInfoService, repository: MasterInfoRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_master = self.repository.get_master_to_process()
        for entity_master in entities_master:
            new_entity_master = self.service.get_master_info(entity_master)
            self.repository.save(new_entity_master)