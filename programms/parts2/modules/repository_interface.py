from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class IRepositoryForSellers(ABC):
    @abstractmethod
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def create_new_seller(self, seller: str) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_sellers_to_process(self) -> List[Dict[str, Any]]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_seller_from_sellerId(self, sellerId: str) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def update_seller_status(self, record: Dict[str, Any], column: str) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
    
class IRepositoryForJunction(ABC):
    @abstractmethod
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def create_new_junction(self, seller_id: int, product_id: int) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
    
class IRepositoryForProductsMaster(ABC):
    @abstractmethod
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def create_new_product(self, asin: str) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_products_to_process(self) -> List[Dict[str, Any]]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_products_to_fill(self) -> List[Dict[str, Any]]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_products_to_image_search(self) -> List[Dict[str, Any]]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_product_from_id(self, id: int) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_product_from_asin(self, asin: str) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def update_product_by_column(self, record: Dict[str, Any], column: str) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def update_product_status(self, record: Dict[str, Any], column: str) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def update_last_search(self, record: Dict[str, Any]) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
    
class IRepositoryForProductsDetail(ABC):
    @abstractmethod
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def create_new_detail(self, product_id: int) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_products_to_process(self) -> List[Dict[str, Any]]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def get_product_from_id(self, id: int) -> Dict[str, Any]:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')

    def update_product_by_column(self, record: Dict[str, Any], column:str) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')
    
class IRepositoryForProductsEc(ABC):
    @abstractmethod
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

    def update_products_ec(self, record: Dict[str, Any]) -> None:
        logging.error("This method is not implemented")
        raise NotImplementedError('This method is not implemented')