import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from google.cloud import vision

from programms.domain.object.dto import EcInfoData

import logging
from typing import List, Optional

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
    
    def search_image(self, image_url: str) -> List[Optional[EcInfoData]]:
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