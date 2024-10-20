from programms.parts3.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction, IRepoForDetail, IRepoForEc
from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.parts3.application.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData
from typing import Union, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UserService:
    def __int__(self) -> None:
        self.repository.sellers = IRepoForSeller()
        self.repository.master = IRepoForMaster()
        self.repository.junction = IRepoForJunction()
        self.reposiory.detail = IRepoForDetail()
        self.repository.ec = IRepoForEc()

## crud
## domain層を出るものはすべてDTO
    # entityになってる
    def exist(self, entity: Union[ESeller, EMaster, EJunction, EDetail, EEc]) -> bool:
        if isinstance(entity, ESeller):
            result = self.repository.sellers.find_by_column(seller = entity.seller.value)
        elif isinstance(entity, EMaster):
            result = self.repository.master.find_by_column(asin = entity.asin.value)
        elif isinstance(entity, EJunction):
            result = self.repository.junction.find_by_column(seller_id = entity.seller_id.value, product_id = entity.product_id.value)
        elif isinstance(entity, EDetail):
            result = self.repository.detail.find_by_column(id = entity.id.value)
        elif isinstance(entity, EEc):
            result = self.repository.ec.find_by_column(id = entity.id.value)
        else:
            raise ValueError('entity type is not defined')
        return result is not None

    def save(self, entity: Union[ESeller, EMaster, EJunction, EDetail, EEc]) -> None:
        if isinstance(entity, ESeller):
            self.repository.sellers.save(SellerData(entity))
        elif isinstance(entity, EMaster):
            self.repository.master.save(MasterData(entity))
        elif isinstance(entity, EJunction):
            self.repository.junction.save(JunctionData(entity))
        elif isinstance(entity, EDetail):
            self.repository.detail.save(DetailData(entity))
        elif isinstance(entity, EEc):
            self.repository.ec.save(EcData(entity))
        else:
            raise ValueError('entity type is not defined')
        
    def find_by_column(self, table_name: str, **kargs) -> List[Union[SellerData, MasterData, JunctionData, DetailData, EcData]]:
        if table_name == 'seller':
            return self.repository.sellers.find_by_column(**kargs)
        elif table_name == 'master':
            return self.repository.master.find_by_column(**kargs)
        elif table_name == 'junction':
            return self.repository.junction.find_by_column(**kargs)
        elif table_name == 'detail':
            return self.repository.detail.find_by_column(**kargs)
        elif table_name == 'ec':
            return self.repository.ec.find_by_column(**kargs)
        else:
            raise ValueError('entity type is not defined')
        
    def delete(self, entity: Union[ESeller, EMaster, EJunction, EDetail, EEc]) -> None:
        if isinstance(entity, ESeller):
            self.repository.sellers.delete(SellerData(entity))
        elif isinstance(entity, EMaster):
            self.repository.master.delete(MasterData(entity))
        elif isinstance(entity, EJunction):
            self.repository.junction.delete(JunctionData(entity))
        elif isinstance(entity, EDetail):
            self.repository.detail.delete(DetailData(entity))
        elif isinstance(entity, EEc):
            self.repository.ec.delete(EcData(entity))
        else:
            raise ValueError('entity type is not defined')

    def to_entity(self, dto: Union[SellerData, MasterData, JunctionData, DetailData, EcData]) -> Union[ESeller, EMaster, EJunction, EDetail, EEc]:
        if isinstance(dto, SellerData):
            return dto._to_entity()
        elif isinstance(dto, MasterData):
            return dto._to_entity()
        elif isinstance(dto, JunctionData):
            return dto._to_entity()
        elif isinstance(dto, DetailData):
            return dto._to_entity()
        elif isinstance(dto, EcData):
            return dto._to_entity()
        else:
            raise ValueError('dto type is not defined')