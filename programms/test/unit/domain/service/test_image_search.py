import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

import unittest

from programms.domain.object.entity import EMaster, EEc
from programms.test.unit.domain.mock_interface.mock_i_client import MockImageSearcher
from programms.domain.service.image_search_service import ImageSearchService

class TestImageSearchService(unittest.TestCase):
    def setUp(self):
        self.mock_image_searcher = MockImageSearcher()
        self.image_search_service = ImageSearchService(image_searcher=self.mock_image_searcher)

    def test_search_image(self) -> bool:
        entity_master = EMaster(id=1, image_url="https://m.media-amazon.com/images/I/test01.jpg")
        results = self.image_search_service.search_image(entity_master)

        id = entity_master.id.value
        expected_results = [
            EEc(product_id=id, ec_url="https://www.ebay.com/itm/test01"),
            EEc(product_id=id, ec_url="https://www.ebay.com/itm/test02"),
            EEc(product_id=id, ec_url='https://www.ebay.com/itm/test03')
        ]

        for i in range(len(results)):
            self.assertEqual(results[i], expected_results[i])

if __name__ == '__main__':
    unittest.main()
