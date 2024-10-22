from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from programms.parts3.application.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class IRepoForSeller(ABC):
    @abstractmethod
    def save(self, seller_dto: SellerData) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    @abstractmethod
    def find_all_by_column(self, sellerid: Optional[str] = None, is_good: Optional[bool] = None) -> List[Dict[str, Any]]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
    
    
class IRepoForJunction(ABC):
    @abstractmethod
    def save(self, junction: JunctionData) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
    
    @abstractmethod
    def find_by_column(self, seller_id: Optional[int] = None, product_id: Optional[int] = None) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

class IRepoForMaster(ABC):
    @abstractmethod
    def save(self, master_dto: MasterData) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

## find by columns
    @abstractmethod
    def find_by_column(self, id: Optional[int] = None, asin: Optional[str] = None, weight: Optional[float] = None, unit: Optional[str] = None, image_url: Optional[str] = None, ec_search: Optional[bool] = None, is_good: Optional[bool] = None, is_filled: Optional[bool] = None) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')


class IRepoForDetail(ABC):
    @abstractmethod
    def save(self, detail_dto: DetailData) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

## find by column
    @abstractmethod
    def find_by_column(self, id: Optional[int] = None, product_id: Optional[int] = None, ec_id: Optional[int] = None, purchase_price: Optional[float] = None, research_date: Optional[datetime] = None, three_month_sales:Optional[int] = None, competitors: Optional[int] = None, import_fees: Optional[float] = None, roi: Optional[float] = None, decision: Optional[bool] = None, final_dicision: Optional[bool] = None, is_filled: Optional[bool] = None) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

class IRepoForEc(ABC):
    @abstractmethod
    def save(self, ec_dto: EcData) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
    
    @abstractmethod
    def find_by_column(self, id: Optional[int] = None, price: Optional[float] = None, is_available: Optional[bool] = None, ec_url: Optional[str] = None, is_filled: Optional[bool] = None, is_supported: Optional[bool] = None) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
