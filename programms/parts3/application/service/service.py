from programms.parts3.domain.service.service import AsinSearchService, SellerSearchService, MasterInfoService, ImageSearchService, EcScrapingService, DetailInfoService

from programms.parts3.application.repository.repository import ApiClientRepo

import logging

class AsinSearch:
    def __init__(self, service: AsinSearchService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def search_asin_by_seller(self, dto_seller) -> None:
        return self.service.search_asin_by_seller(dto_seller)
    
class SellerSearch:
    def __init__(self, service: SellerSearchService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def search_seller_by_asin(self, dto_master) -> None:
        return self.service.search_seller_by_asin(dto_master)
    
class MasterInfo:
    def __init__(self, service: MasterInfoService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def get_master_info(self, dto_master) -> None:
        return self.service.get_master_info(dto_master)
    
class ImageSearch:
    def __init__(self, service: ImageSearchService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def search_image(self, dto_master) -> None:
        return self.service.search_image(dto_master)
    
class EcScraping:
    def __init__(self, service: EcScrapingService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def scrape(self, dto_ec) -> None:
        return self.service.scrape(dto_ec)
    
class DetailInfo:
    def __init__(self, service: DetailInfoService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def get_detail_info(self, dto_detail) -> None:
        return self.service.get_detail_info(dto_detail)
    
class AsinEvaluate:
    def __init__(self, service: AsinEvaluateService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def evaluate_asin(self, dto_master) -> None:
        return self.service.evaluate_asin(dto_master)
    
    def evaluate_products(self) -> None:
        logging.info("Evaluating products")
        products = self.repository.get_products_to_evaluate()
        for product in products:
            decisions = self.repository.get_decisions(product['id'])
            if sum(d['decision'] for d in decisions) > 1:
                self.repository.update_product_is_good(product['id'])

    
class SellerEvaluate:
    def __init__(self, service: SellerEvaluateService, repo: ApiClientRepo) -> None:
        self.service = service
        self.repo = repo

    def evaluate_seller(self, dto_seller) -> None:
        return self.service.evaluate_seller(dto_seller)
    
    def evaluate_sellers(self) -> None:
        logging.info("Evaluating sellers")
        sellers = self.repository.get_sellers_to_evaluate()
        for seller in sellers:
            result = self.repository.get_seller_products(seller['id'])
            if result[0]['total'] == 0:
                continue
            p = result[0]['num'] / result[0]['total'] 
            print(p)
            if p > 0.3:
                self.repository.update_seller_is_good(seller['id'])
