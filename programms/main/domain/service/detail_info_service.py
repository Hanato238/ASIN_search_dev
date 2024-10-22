from programms.main.domain.interface.i_api_client import IKeepaClient, IAmazonAPIClient
from programms.main.domain.object.entity import EDetail
from programms.main.domain.service.crud_service import DomainService

from typing import List, Optional

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