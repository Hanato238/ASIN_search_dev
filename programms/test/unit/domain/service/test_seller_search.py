import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

import unittest

from programms.domain.object.entity import ESeller, EMaster, EJunction
from programms.test.unit.domain.mock_interface.mock_i_client import MockKeepaClient
from programms.domain.service.seller_search_service import SellerSearchService

class TestSellerSearchService(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_keepa_client = MockKeepaClient()
        self.seller_search_service = SellerSearchService(keepa_client=self.mock_keepa_client)

    def test_search_seller_by_asin(self) -> None:
        # テストデータ
        entity_master = EMaster(id=1, asin='B0TEST0001')
        sellers = ['SELLERIDTEST01', 'SELLERIDTEST02', 'SELLERIDTEST03']

        result = self.seller_search_service.search_seller_by_asin(entity_master)

        expected_result = []
        for seller in sellers:
            expected_seller = ESeller(seller=seller)
            expected_juction = EJunction(product_id=entity_master.id.value, seller=seller, asin=entity_master.asin.value)
            expected_result.append((expected_seller, expected_juction))

        for i in range(len(result)):
            self.assertEqual(result[i][0], expected_result[i][0])
            self.assertEqual(result[i][1], expected_result[i][1])

if __name__ == '__main__':
    unittest.main()