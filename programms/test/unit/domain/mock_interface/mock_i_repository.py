import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

from unittest.mock import MagicMock

from programms.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction, IRepoForDetail, IRepoForEc
from programms.application.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData

from typing import Optional, List
import logging


class MockRepoForSeller(MagicMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(spec=IRepoForSeller, *args, **kwargs)

    def save(self, seller_dto: SellerData) -> None:
        return super().save(seller_dto)

    def find_by_column(self, sellerid: Optional[str] = None, is_good: Optional[bool] = None) -> Optional[SellerData]:
        result = ESeller(id=1, seller='test', is_good=True)
        return result
    
class MockRepoForMaster(MagicMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(spec=IRepoForMaster, *args, **kwargs)

    def save(self, master_dto: MasterData) -> None:
        return super().save(master_dto)
    
    def find_by_column(self, id: Optional[int] = None, asin: Optional[str] = None, weight: Optional[float] = None, unit: Optional[str] = None, image_url: Optional[str] = None, ec_search: Optional[bool] = None, is_good: Optional[bool] = None, is_filled: Optional[bool] = None) -> Optional[MasterData]:
        result = EMaster(id=1, asin='test', weight=1.0, unit='kg', image_url='test', ec_search=True, is_good=True, is_filled=True)
        return result
    
class MockRepoForJunction(MagicMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(spec=IRepoForJunction, *args, **kwargs)

    def save(self, junction: JunctionData) -> None:
        return super().save(junction)
    
    def find_by_column(self, seller_id: Optional[int] = None, product_id: Optional[int] = None) -> Optional[JunctionData]:
        result = EJunction(seller_id=1, product_id=1)
        return result
    
class MockRepoForDetail(MagicMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(spec=IRepoForDetail, *args, **kwargs)

    def save(self, detail_dto: DetailData) -> None:
        return super().save(detail_dto)
    
    def find_by_column(self, id: Optional[int] = None, product_id: Optional[int] = None, ec_id: Optional[int] = None, purchase_price: Optional[float] = None, research_date: Optional[str] = None, three_month_sales:Optional[int] = None, competitors: Optional[int] = None, import_fees: Optional[float] = None, roi: Optional[float] = None, decision: Optional[bool] = None, final_dicision: Optional[bool] = None, is_filled: Optional[bool] = None) -> Optional[DetailData]:
        result = EDetail(id=1, product_id=1, ec_id=1, purchase_price=1.0, research_date='2021-01-01', three_month_sales=1, competitors=1, import_fees=1.0, roi=1.0, decision=True, final_dicision=True, is_filled=True)
        return result
    
class MockRepoForEc(MagicMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(spec=IRepoForEc, *args, **kwargs)

    def save(self, ec_dto: EcData) -> None:
        return super().save(ec_dto)
    
    def find_by_column(self, id: Optional[int] = None, ec_name: Optional[str] = None, is_good: Optional[bool] = None, is_filled: Optional[bool] = None) -> List[Optional[EcData]]:
        result = List[
            EEc(id=1, product_id=1, asin='B0TEST0001', ec_name='https://www.ebay.com/itm/test01', price=100.0, currency='USD', is_good=True, is_filled=True),
            EEc(id=2, product_id=1, asin='B0TEST0002', ec_name='https://www.ebay.com/itm/test02', price=150.0, currency='USD', is_good=True, is_filled=True),
            EEc(id=3, product_id=1, asin='B0TEST0003', ec_name='https://www.ebay.com/itm/test03', price=200.0, currency='EUR', is_good=True, is_filled=True)
        ]
        return result
    
    