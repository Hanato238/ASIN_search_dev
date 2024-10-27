from programms.main.domain.object.dto import SellerInfoData, MasterInfoData, DetailSalesData, DetailCommissionData, EcInfoData, ScrapingInfoData

from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class IKeepaClient(ABC):
    @abstractmethod
    def search_asin_by_seller(self, seller: str) -> List[str]:
        pass

    @abstractmethod
    def query_seller_info(self, asin: str) -> Dict[SellerInfoData]:
        pass

    @abstractmethod
    def get_sales_rank_drops(self, asin: str) -> Optional[int]:
        pass

class IAmazonAPIClient(ABC):
    @abstractmethod
    def request_product_details(self, asin: str) -> Optional[MasterInfoData]:
        pass

    @abstractmethod
    def request_product_price(self, asin: str) -> Optional[DetailSalesData]:
        pass

    @abstractmethod
    def request_product_commission(self, asin: str, price: float) -> Optional[DetailCommissionData]:
        pass

class IImageSearcher(ABC):
    @abstractmethod
    def search_image(self, image_url: str) -> List[Optional[EcInfoData]]:
        pass


class IScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> List[Optional[ScrapingInfoData]]:
        pass

class IGasClient(ABC):
    @abstractmethod
    def read_from_spreadsheet(self, spreadsheet_id: str, range_name: str) -> List[Any]:
        pass

    @abstractmethod
    def write_to_spreadsheet(self, spreadsheet_id: str, range_name: str, data: List[Any]) -> None:
        pass