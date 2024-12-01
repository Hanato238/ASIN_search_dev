import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

import unittest
from unittest.mock import MagicMock

from programms.domain.object.entity import EMaster, EEc
from programms.domain.object.dto import MasterInfoData
from programms.test.unit.domain.mock_interface.mock_i_client import MockAmazonAPIClient
from programms.domain.service.master_info_service import MasterInfoService

class TestMasterInfoService(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_amazon_api_client = MockAmazonAPIClient()
        self.master_info_service = MasterInfoService(amazon_api_client=self.mock_amazon_api_client)

    def test_master_info(self):
        entity_master = EMaster(id=1, asin="B0TEST0001")
        result = self.master_info_service.get_master_info(entity_master)

        # 検証
        expected_result = EMaster(
            id = 1,
            asin = "B0TEST0001",
            weight = 1.0,
            weight_unit = 'kilogram',
            image_url = 'https://m.media-amazon.com/images/I/image.jpg',
        )
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()