from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IKeepaClient(ABC):
    @abstractmethod
    def search_asin_by_seller(self, seller: str) -> List[str]:
        pass

    @abstractmethod
    def query_seller_info(self, asin: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_sales_rank_drops(self, asin: str) -> Dict[str, Any]:
        pass

class IAmazonAPIClient(ABC):
    @abstractmethod
    def request_product_details(self, record: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def request_product_price(self, asin: str) -> float:
        pass

    @abstractmethod
    def request_product_fees(self, asin: str, price: float) -> float:
        pass

class IImageSearcher(ABC):
    @abstractmethod
    def search_image(self, image_url: str) -> List[str]:
        pass


class IScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> Dict[str, Any]:
        pass