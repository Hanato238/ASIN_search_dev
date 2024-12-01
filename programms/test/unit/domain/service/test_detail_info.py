import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

import unittest

from programms.domain.object.entity import ESeller, EMaster, EJunction, EDetail
from programms.test.unit.domain.mock_interface.mock_i_client import MockKeepaClient, MockAmazonAPIClient
from programms.test.unit.domain.mock_interface.mock_i_repository import MockRepoForEc
from programms.domain.service.detail_info_service import DetailInfoService
from programms.domain.service.domain_service import DomainService

class TestDetailInfoService(unittest.TestCase):
    def setUp(self):
        self.mock_keepa_client = MockKeepaClient()
        self.mock_amazon_api_client = MockAmazonAPIClient()
        self.detail_info_service = DetailInfoService(keepa_client=self.mock_keepa_client, 
                                                     sp_api_client=self.mock_amazon_api_client, 
                                                     domain_service=DomainService(MockRepoForEc))

    def test_search_detail(self):
        entity_detail = EDetail(asin='B0TEST0001')
        result = self.detail_info_service.search_detail(entity_detail)

        expected_result = EDetail(
            asin = 'B0TEST0001',
            three_month_sales = 5,
            competitors = 2,
            sales_price = 1000.0,
            comission = 100.0,
            purchase_price = 1000,
            import_fees = 100,
            roi = 10
        )
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()