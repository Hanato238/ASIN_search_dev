import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.service.crud_service import UserService
from programms.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.application.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData
from typing import Union, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class useCase:
    def __int__(self) -> None:
        self.user_service = UserService()

    ## command objectにすべき？
    def save(self, entity: Union[ESeller, EMaster, EJunction, EDetail, EEc]) -> None:
        if self.user_service.exist(entity):
            self.user_service.save(entity)
            logging.info('This entity is saved')
        else:
            logging.error('This entity is already exist')

    def find_by_column(self, table_name: str, **kargs) -> List[Union[SellerData, MasterData, JunctionData, DetailData, EcData]]:
        return self.user_service.find_by_column(table_name, **kargs)
    
    def delete(self, entity: Union[ESeller, EMaster, EJunction, EDetail, EEc]) -> None:
        if self.user_service.exist(entity):
            self.user_service.delete(entity)
            logging.info('This entity is deleted')
        else:
            logging.error('This entity is not exist')