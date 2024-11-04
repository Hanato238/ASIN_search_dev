from programms.parts3.domain.service._service import AsinSearchService, SellerSearchService, MasterInfoService, ImageSearchService, EcScrapingService, DetailInfoService

from programms.parts3.application.repository.repository import AsinSearchRepo, SellerSearchRepo, MasterInfoRepo, EcScrapingRepo, DetailInfoRepo

import logging

class AsinSearch:
    def __init__(self, service: AsinSearchService, repository: AsinSearchRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_seller = self.repository.get_seller_to_process()
        for entity_seller in entities_seller:
            data = self.service.search_asin_by_seller(entity_seller.seller.value)
            for datum in data:
                for entity in datum:
                    self.repository.save(entity)
                    # junctionは?
class SellerSearch:
    def __init__(self, service: SellerSearchService, repository: SellerSearchRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_master = self.repository.get_master_to_process()
        for entity_master in entities_master:
            data = self.service.search_seller_by_asin(entity_master.asin.value)
            for datum in data:
                for entity in datum:
                    self.repository.save(entity)
                    # junctionは?

# 下記2つはまとめてもよいのでは？
class MasterInfo:
    def __init__(self, service: MasterInfoService, repository: MasterInfoRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_master = self.repository.get_master_to_process()
        for entity_master in entities_master:
            new_entity_master = self.service.get_master_info(entity_master)
            self.repository.save(new_entity_master)
    
class ImageSearch:
    def __init__(self, service: ImageSearchService, repository: MasterInfoRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        entities_master = self.repository.get_master_to_image_search()
        for entity_master in entities_master:
            entities_ec = self.service.search_image(entity_master.image_url.value)
            for entity_ec in entities_ec:
                self.repository.save(entity_ec)
    
class EcScraping:
    def __init__(self, service: EcScrapingService, repository: EcScrapingRepo) -> None:
        self.service = service
        self.repository = repository

    def run(self, dto_ec) -> None:
        entities_ec = self.repository.get_ec_to_process()
        for entity_ec in entities_ec:
            new_entity_ec = self.service.scrape_ec(entity_ec.ec_url.value)
            self.repository.save(new_entity_ec)

class DetailInfo:
    def __init__(self, service: DetailInfoService, repo: DetailInfoRepo) -> None:
        self.service = service
        self.repo = repo

    def run(self) -> None:
        entities_detail = self.repository.get_detail_to_process()
        for entity_detail in entities_detail:
            new_entity_detail = self.service.get_detail_info(entity_detail)
            self.repository.save(new_entity_detail)
    

"""
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
"""