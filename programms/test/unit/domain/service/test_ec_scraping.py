import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

import unittest

from programms.domain.object.entity import EEc
from programms.domain.object.dto import ScrapingInfoData
from programms.test.unit.domain.mock_interface.mock_i_client import MockScraper
from programms.domain.service.ec_scraping_service import EcScrapingService


class TestEcScrapingService(unittest.TestCase):
    def setUp(self):
        self.mock_scraper = MockScraper()
        self.ec_scraping_service = EcScrapingService(scraper=self.mock_scraper)

    def test_scrape_ec(self):
        entity_ec = EEc(ec_url='https://www.ebay.com/itm/test01')
        result = self.ec_scraping_service.scrape_ec(entity_ec)

        # 検証
        expected_result = [
            ScrapingInfoData({
                'price': 1000.0,
                'currency': 'JPY',
                'is_available': True
            }).update_entity(entity_ec),
            ScrapingInfoData({
                'price': 2000.0,
                'currency': 'JPY',
                'is_available': False
            }).update_entity(entity_ec),
            ScrapingInfoData({
                'price': 3000.0,
                'currency': 'JPY',
                'is_available': True
            }).update_entity(entity_ec)
        ]

        for i in range(len(result)):
            self.assertEqual(result[i], expected_result[i])

if __name__ == '__main__':
    unittest.main()