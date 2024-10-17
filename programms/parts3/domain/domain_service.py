from programms.parts3.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction, IRepoForDetail, IRepoForEc
from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.parts3.domain.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData
from typing import Union, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DomainService:
    def __int__(self) -> None:
        self.repository.sellers = IRepoForSeller()
        self.repository.master = IRepoForMaster()
        self.repository.junction = IRepoForJunction()
        self.reposiory.detail = IRepoForDetail()
        self.repository.ec = IRepoForEc()

## crud
## repositoryに渡すのはDTO
    def exist(self, entity: Union[ESeller, EMaster, EJunction, EDetail, EEc]) -> bool:
        if isinstance(entity, ESeller):
            return self.repository.sellers.find_by_column(entity.id.value)
        elif isinstance(entity, EMaster):
            return self.repository.master.exist(entity)
        elif isinstance(entity, EJunction):
            return self.repository.junction.exist(entity)
        elif isinstance(entity, EDetail):
            return self.repository.detail.exist(entity)
        elif isinstance(entity, EEc):
            return self.repository.ec.exist(entity)
        else:
            raise ValueError('entity type is not defined')
        
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
        
    def find_by_column(self, table_name: str, **kargs) -> Union[ESeller, EMaster, EJunction, EDetail, EEc]:
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
            self.repository.sellers.delete(entity)
        elif isinstance(entity, EMaster):
            self.repository.master.delete(entity)
        elif isinstance(entity, EJunction):
            self.repository.junction.delete(entity)
        elif isinstance(entity, EDetail):
            self.repository.detail.delete(entity)
        elif isinstance(entity, EEc):
            self.repository.ec.delete(entity)
        else:
            raise ValueError('entity type is not defined')


    def to_entity(self, dto: Union[SellerData, MasterData, JunctionData, DetailData, EcData]) -> Union[ESeller, EMaster, EJunction, EDetail, EEc]:
        if isinstance(dto, SellerData):
            return dto.to_entity()
        elif isinstance(dto, MasterData):
            return dto.to_entity()
        elif isinstance(dto, JunctionData):
            return dto.to_entity()
        elif isinstance(dto, DetailData):
            return dto.to_entity()
        elif isinstance(dto, EcData):
            return dto.to_entity()
        else:
            raise ValueError('dto type is not defined')

        

## application層にentity classは返さない。DTOを返す
## repositoryからの戻り値もDTOがよい
    def get_products_to_asin_search(self) -> Dict[ESeller]:
        entities = self.repository.sellers.find_by_column(is_good = True)
        dtos = [SellerData(entity) for entity in entities]
        return dtos

    def get_products_to_seller_search(self) -> Dict[EMaster]:
        entities = self.repository.master.find_by_column(is_good = True)
        dtos = [MasterData(entity) for entity in entities]
        return dtos

    def get_products_to_image_search(self) -> Dict[EMaster]:
        entities = self.repository.master.find_by_column(ec_ecarch = False)
        dtos = [MasterData(entity) for entity in entities]
        return dtos

    def get_products_to_fill_master(self) -> Dict[EMaster]:
        entities = self.repository.master.find_by_column(is_filled = False)
        dtos = [MasterData(entity) for entity in entities]
        return dtos
    
    def get_products_to_fill_ec(self) -> Dict[EEc]:
        entities = self.repository.ec.find_by_column(is_filled = False)
        dtos = [EcData(entity) for entity in entities]
        return dtos
    
    def get_products_to_fill_detail(self) -> Dict[EDetail]:
        entities = self.repository.detail.find_by_column(is_filled = False)
        dtos = [DetailData(entity) for entity in entities]
        return dtos
    
    
## for API client
    def search_products_by_seller(self, seller:SellerData) -> Dict[MasterData]:
        data_asins = self.keepa_client.search_asin_by_seller(seller.seller.value)
        dtos = []
        for data_asin in data_asins:
            dto = MasterData(asin = data_asin)
            dtos.append(dto)
        return dtos
    
    def search_sellers_by_product(self, master: MasterData) -> Dict[SellerData]:
        data_sellers = self.keepa_client.query_seller_info(master.asin.value)
        dtos = []
        for datum in data_sellers:
            dto = SellerData(seller = datum['seller'])
            dtos.append(dto)
        return dtos
    
    def search_competitors_by_seller(self, master: MasterData) -> Dict[Any]:
        data_sellers = self.keepa_client.query_seller_info(master.asin.value)
        competitors = 0
        for datum in data_sellers:
            if datum.is_competitor():
                competitors += 1
        return competitors

    def search_three_month_sales(self, asin:str) -> Dict[EMaster]:
        data_sales = self.keepa_client.get_sales_rank_drops(asin)
        dtos = []
        for data_sale in data_sales:
            dto = MasterData(three_month_sales = data_sale)
            dtos.append(dto)
        return dtos


# for filling Detail
class CalculateService:
    def __int__(self) -> None:
        self.repository.sellers = IRepoForSeller()
        self.repository.master = IRepoForMaster()
        self.repository.junction = IRepoForJunction()
        self.reposiory.detail = IRepoForDetail()
        self.repository.ec = IRepoForEc()

    def compare_product_price(self, entity: EDetail) -> EDetail:
        if entity.product_id is not None:
            return entity
        entities_ec = self.repository.ec.find_all_by_product_id(entity.product_id)
        min_price = float('inf')
        min_price_product = {'ec_id': None, 'price': None}
        for entity_ec in entities_ec:
            price = entity_ec.price.convert_to_jpy()
            if price < min_price:
                min_price = price
                min_price_product = {'ec_id': entity_ec.id, 'price': price}
        entity.purchase_price = min_price_product['price']
        entity.ec_id = min_price_product['ec_id']
        return entity
    
    def calculate_import_fees(self, entity: EDetail) -> EDetail:
        if entity.purchase_price is None:
            raise ValueError('purchase_price is None')
        import_tax = entity.purchase_price * 0.1

        entity_master = self.repository.master.find_by_id(entity.product_id)
        weight = entity_master.weight.convert_to_gram().value()
        transfar_fees = weight * 2

        entity.import_fees = import_tax + transfar_fees
        return entity

            

    def evaluate_product(self, entity: EMaster) -> None:
        return

    def evaluate_seller(self, entity: ESeller) -> None:
        return