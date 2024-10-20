from programms.parts3.domain.interface.i_api_client import IKeepaClient, IAmazonAPIClient, IImageSearcher, IScraper
from programms.parts3.domain.interface.i_repository import IRepoForEc
from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc

from programms.parts3.application.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData

from typing import List

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

    def search_image(self, entity_master: EMaster) -> List[EcData]:
        data = []
        ec_urls = self.image_searcher.search_image(entity_master.image_url.value)
        for ec_url in ec_urls:
            entity_ec = EEc(product_id=entity_master.id.value, ec_url=ec_url)
            data.append(entity_ec)
        return data
    
class EcScrapingService:
    def __init__(self, scraper: IScraper) -> None:
        self.scraper = scraper

    def scrape_ec(self, dto_ec: EcData) -> None:
        # ec_data: Dict[str, Any]
        ec_data = self.scraper.scrape_ec(dto_ec.ec_url)
        dto_ec.price = ec_data['price']
        dto_ec.currency = ec_data['currency']
        dto_ec.is_available = ec_data['is_available']
        return dto_ec
    
class DetailInfoService:
    def __init__(self, keepa_client: IKeepaClient, sp_api_client: IAmazonAPIClient, repo_master: IRepoForMaster, repo_ec: IRepoForEc) -> None:
        self.keepa_client = keepa_client
        self.sp_api_client = sp_api_client
        self.repository.master = repo_master
        self.repository.ec = repo_ec

    def search_detail(self, dto_detail: DetailData) -> None:
        if dto_detail.three_month_sales is None:
            dto_detail.three_month_sales = self.keepa_client.get_three_month_sales(dto_detail.asin)
        if dto_detail.competitors is None:
            dto_detail.competitors = self.keepa_client.get_competitors(dto_detail.asin)
        
        if dto_detail.commission is None:
            dto_detail.commission = self.sp_api_client.request_product_fees(dto_detail.asin)
        if dto_detail.sales_price is None:
            dto_detail.sales_price = self.sp_api_client.request_product_price(dto_detail.asin)

        if dto_detail.purchase_price is None:
            dto_detail.purchase_price, dto_detail.ec_id = self.compare_product_price(dto_detail.product_id)

        entity_detail = dto_detail._to_entity

        if dto_detail.import_fees is None:
            dto_detail.import_fees = entity_detail.calc_import_fees()
        if dto_detail.roi is None:
            dto_detail.roi = entity_detail.calc_roi()

        return dto_detail


    def compare_product_price(self, entity: EDetail) -> EDetail:
        if entity.product_id is not None:
            return entity
        entities_ec = self.repository.ec.find_by_column(product_id=entity.product_id)
        min_price = float('inf')
        min_price_product = {'ec_id': None, 'price': None}
        for entity_ec in entities_ec:
            price = entity_ec.price.convert_to_jpy()
            if price < min_price:
                min_price = price

                min_price_product = {'ec_id': entity_ec.id, 'price': price}
        entity.purchase_price = min_price_product['price']
        entity.ec_id = min_price_product['ec_id']
        return entity