import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))


import unittest

from programms.domain.object.entity import ESeller, EMaster, EJunction, EDetail
from programms.test.unit.domain.mock_interface.mock_i_client import MockKeepaClient
from programms.domain.service.asin_search_service import AsinSearchService

class TestAsinSearchService(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_keepa_client = MockKeepaClient()
        self.asin_search_service = AsinSearchService(keepa_client=self.mock_keepa_client)

    def test_search_asin_by_seller(self) -> bool:
        # テストデータ
        entity_seller = ESeller(id=1, seller='SELLERIDTEST01')
        asins = ['B0TEST0001', 'B0TEST0002', 'B0TEST0003']
        #['https://www.ebay.com/itm/test_1', 'https://www.ebay.com/itm/test_1', 'https://www.ebay.com/itm/test_1']
#        self.mock_keepa_client.search_asin_by_seller.return_value = asins

        result = self.asin_search_service.search_asin_by_seller(entity_seller)

        expected_result = []
        for asin in asins:
            expected_juction = EJunction(seller_id=1, seller=entity_seller.seller.value, asin=asin)
            expected_detail = EDetail(asin=asin)
            expected_result.append((EMaster(asin=asin), expected_juction, expected_detail))

        for i in range(len(result)):
            self.assertEqual(result[i][0], expected_result[i][0])
            self.assertEqual(result[i][1], expected_result[i][1])
            self.assertEqual(result[i][2], expected_result[i][2])


if __name__ == '__main__':
    unittest.main()