from google.cloud import vision

from programms.parts3.infrastructure.object.dto import EcInfoData

import logging
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class ImageSearcher:
    _instance = None
    _POSITIVE_LIST = {
        'amazon': 'amazon',
        'walmart': 'walmart',
        'ebay': 'ebay'
    }

    def __new__(cls) -> 'ImageSearcher':
        if cls._instance is None:

            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize(self) -> None:
        self.client = vision.ImageAnnotatorClient()
        # positive list + negative list方式にする? : positive list方式 + salvage方式にする
    
    def search_image(self, image_url: str) -> List[EcInfoData, None]:
        logging.info(f"Searching image from {image_url}")
        if image_url == None:
            logging.info("No image URL found")
            return None
        image = vision.Image()

        image.source.image_uri = image_url
        response = self.client.web_detection(image=image)
        annotations = response.web_detection
        data = []

        if annotations.pages_with_matching_images:
            for page in annotations.pages_with_matching_images:
                    if any(domain in page.url for domain in self._POSITIVE_LIST):
                        data.append(EcInfoData(page.url))

        logging.info(f"Found {len(data)} matching URLs")
        return data
    


"""
# 正規表現が厳密にわかれば使用
            try:
                if self.check_urls(ec_url):
                    self.update.update_ec_url(record_product_ec)
                else:
                    self.update.update_salvage_ec(record_product_ec)
                    logging.info("URL not supported")
            except Exception as e:
                logging.info("An error occurred: {e}")
                continue
"""