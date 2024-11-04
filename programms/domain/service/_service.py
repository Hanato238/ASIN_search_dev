from programms.main.domain.interface.i_api_client import IKeepaClient, IAmazonAPIClient, IImageSearcher, IScraper
from programms.main.domain.interface.i_repository import IRepoForEc
from programms.main.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.main.domain.service.crud_service import DomainService

from typing import List, Optional

class AsinSearchService:
    def __init__(self, keepa_client: IKeepaClient) -> None:
        self.keepa_client = keepa_client

    def search_asin_by_seller(self, entity_seller: ESeller) -> List[(EMaster, EJunction, EDetail)]:
        data = []
        entities_master = self.keepa_client.search_asin_by_seller(entity_seller.seller.value)
        # asinsの型
        for entity_master in entities_master:
            entity_junction = EJunction(seller_id=entity_seller.id.value, product_id=entity_master.id.value, seller=entity_seller.seller.value, asin=entity_master.asin.value)
            entity_detail = EDetail(id=entity_master.id.value, asin=entity_master.asin.value)
            datum = (entity_master, entity_junction, entity_detail)
            data.append(datum)
        return data
    
class SellerSearchService:
    def __init__(self, keepa_client: IKeepaClient) -> None:
        self.keepa_client = keepa_client
        
    def search_seller_by_asin(self, entity_master: EMaster) -> List[(ESeller, EJunction)]:
        data = []
        sellers = self.keepa_client.query_seller_info(entity_master.asin.value)
        # sellers: List[str]
        for seller in sellers:
            entity_seller = ESeller(seller=seller)
            # error("seller_id=None")
            entity_junction = EJunction(seller_id=entity_seller.id.value, product_id=entity_master.id.value, seller=entity_seller.seller.value, asin=entity_master.asin.value)
            datum = (entity_seller, entity_junction)
            data.append(datum)
        return data
    
class MasterInfoService:
    def __init__(self, amazon_api_client: IAmazonAPIClient) -> None:
        self.amazon_api_client = amazon_api_client

    def get_master_info(self, entity_master: EMaster) -> EMaster:
        data = self.amazon_api_client.request_product_details(entity_master.asin.value)
        new_entity_master = data.update_entity(entity_master)
        return new_entity_master
    
class ImageSearchService:
    def __init__(self, image_searcher: IImageSearcher) -> None:
        self.image_searcher = image_searcher

    def search_image(self, entity_master: EMaster) -> List[EEc]:
        entities_ec = []
        ec_urls = self.image_searcher.search_image(entity_master.image_url.value)
        for ec_url in ec_urls:
            entity_ec = EEc(product_id=entity_master.id.value, ec_url=ec_url)
            entities_ec.append(entity_ec)
        return entities_ec
    
class EcScrapingService:
    def __init__(self, scraper: IScraper) -> None:
        self.scraper = scraper

    def scrape_ec(self, entity_ec: EEc) -> List[Optional[EEc]]:
        # ec_data: Dict[str, Any]
        ec_data = self.scraper.scrape_ec(entity_ec.ec_url.value)
        entities_ec = []
        for ec_datum in ec_data:
            new_entity_ec = entity_ec.update_entity(ec_datum)
            entities_ec.append(new_entity_ec)
        return entities_ec
    
class DetailInfoService:
    def __init__(self, keepa_client: IKeepaClient, sp_api_client: IAmazonAPIClient) -> None:
        self.keepa_client = keepa_client
        self.sp_api_client = sp_api_client
        self.domain_service = DomainService()

    def search_detail(self, entity_detail: EDetail) -> None:
        # by KeepaAPI
        if entity_detail.three_month_sales.value is None:
            three_month_sales = self.keepa_client.get_three_month_sales(entity_detail.asin.value)
            entity_detail.three_month_sales.value(three_month_sales)
        if entity_detail.competitors.value is None:
            competitors = self.keepa_client.get_competitors(entity_detail.asin.value)
            entity_detail.competitors.value(competitors)
        # by AmazonAPI
        if entity_detail.sales_price.value is None:
            sales_price = self.sp_api_client.request_product_price(entity_detail.asin.value)
            entity_detail.sales_price.value(sales_price)
        if entity_detail.comission.value is None:
            commission = self.sp_api_client.request_product_fees(entity_detail.asin.value, entity_detail.sales_price.amount)
            entity_detail.comission.value(commission)
        # by DomainService
        if entity_detail.purchase_price is None:
            data = self.domain_service.compare_product_price(entity_detail.product_id.value)
            entity_detail.ec_id.value(data['ec_id'])
            entity_detail.purchase_price.value(data['price'])
        # by entity method
        if entity_detail.import_fees is None:
            import_fees = entity_detail.calc_import_fees()
            entity_detail.import_fees.amount(import_fees)
        if entity_detail.roi is None:
            roi = entity_detail.calc_roi()
            entity_detail.roi.value(roi)

        return entity_detail


