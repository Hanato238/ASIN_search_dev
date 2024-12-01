import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

from unittest.mock import MagicMock

from programms.domain.object.dto import SellerInfoData, MasterInfoData, DetailSalesData, DetailCommissionData, EcInfoData, ScrapingInfoData
from programms.domain.interface.i_api_client import IKeepaClient, IAmazonAPIClient, IImageSearcher, IScraper, IGasClient

from typing import List, Dict, Optional, Any

class MockKeepaClient(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(spec=IKeepaClient, *args, **kwargs)

    def search_asin_by_seller(self, seller: str) -> Optional[List[str]]:
        return ['B0TEST0001', 'B0TEST0002', 'B0TEST0003']

    def query_seller_info(self, asin: str) -> Optional[List[SellerInfoData]]:
        return [
            SellerInfoData({
                "sellerId": "SELLERIDTEST01",
                "isFBA": True,
                "condition": "New",
                "isShippable": True,
                "isPrime": False,
                "isAmazon": False,
                "isScam": False
            }),
            SellerInfoData({
                "sellerId": "SELLERIDTEST02",
                "isFBA": False,
                "condition": "Used",
                "isShippable": False,
                "isPrime": True,
                "isAmazon": False,
                "isScam": True
            }),
            SellerInfoData({
                "sellerId": "SELLERIDTEST03",
                "isFBA": True,
                "condition": "New",
                "isShippable": True,
                "isPrime": False,
                "isAmazon": False,
                "isScam": False
            })
        ]
    
    def get_three_month_sales(self, asin: str) -> Optional[int]:
        return 5
    
class MockAmazonAPIClient(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(spec=IAmazonAPIClient, *args, **kwargs)

    def request_product_details(self, asin: str) -> Optional[MasterInfoData]:
        return MasterInfoData({
            'asin': asin,
            'weight': 1.0,
            'weight_unit': 'kilogram',
            'image_url': 'https://m.media-amazon.com/images/I/image.jpg',
        })
    
    def request_product_price(self, asin: str) -> Optional[DetailSalesData]:
        return DetailSalesData({
            'asin': asin,
            'price': 1000.0,
            'currency': 'JPY',
        })
    
    def request_product_fees(self, asin: str, price: float) -> Optional[DetailCommissionData]:
        return DetailCommissionData({
            'asin': asin,
            'commission': 100.0,
            'currency': 'JPY',
        })
    
class MockImageSearcher(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(spec=IImageSearcher, *args, **kwargs)

    def search_image(self, image_url: str) -> Optional[List[EcInfoData]]:
        return [
            EcInfoData(ec_url='https://www.ebay.com/itm/test01'),
            EcInfoData(ec_url='https://www.ebay.com/itm/test02'),
            EcInfoData(ec_url='https://www.ebay.com/itm/test03')
        ]
    
class MockScraper(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(spec=IScraper, *args, **kwargs)

    def scrape_ec(self, url: str) -> Optional[List[ScrapingInfoData]]:
        return [
            ScrapingInfoData({
                'price': 1000.0,
                'currency': 'JPY',
                'is_available': True
            }),
            ScrapingInfoData({
                'price': 2000.0,
                'currency': 'JPY',
                'is_available': False
            }),
            ScrapingInfoData({
                'price': 3000.0,
                'currency': 'JPY',
                'is_available': True
            })
        ]
    
# yet maybe pandas dataframe is required
class MockGasClient(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(spec=IGasClient, *args, **kwargs)

    def read_from_spreadsheet(self, spreadsheet_id: str, range_name: str) -> List[Any]:
        return [['test1', 'test2', 'test3'], ['test4', 'test5', 'test6']]

    def write_to_spreadsheet(self, spreadsheet_id: str, range_name: str, data: List[Any]) -> None:
        pass