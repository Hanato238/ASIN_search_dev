import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from programms.domain.interface.i_api_client import IKeepaClient, IAmazonAPIClient
from programms.domain.object.entity import EDetail
from programms.domain.service.domain_service import DomainService

from typing import Any

class DetailInfoService:
    def __init__(self, keepa_client: IKeepaClient, sp_api_client: IAmazonAPIClient) -> None:
        self.keepa_client = keepa_client
        self.sp_api_client = sp_api_client
        self.domain_service = domain_service

    def search_detail(self, entity_detail: EDetail) -> EDetail:
        entity_detail = self._update_from_keepa(entity_detail)
        entity_detail = self._update_from_sp_api(entity_detail)
        entity_detail = self._update_from_domain_service(entity_detail)
        entity_detail = self._update_from_entity_method(entity_detail)
        return entity_detail
    
    def _update_from_keepa(self, entity_detail: EDetail) -> EDetail:
        if entity_detail.three_month_sales.value is None:
            three_month_sales = self.keepa_client.get_three_month_sales(entity_detail.asin.value)
            entity_detail.update_three_month_sales(three_month_sales)
        if entity_detail.competitors.value is None:
            competitors = self.keepa_client.query_seller_info(entity_detail.asin.value)
            num_competitors = self.domain_service.count_competitors(competitors)
            entity_detail.update_competitors(num_competitors)
        return entity_detail
    
    def _update_from_sp_api(self, entity_detail: EDetail) -> EDetail:
        if entity_detail.sales_price.amount is None:
            sales_datum = self.sp_api_client.request_product_price(entity_detail.asin.value)
            sales_datum.update_entity(entity_detail)
        if entity_detail.commission.amount is None:
            commission_datum = self.sp_api_client.request_product_fees(entity_detail.asin.value, entity_detail.sales_price.amount)
            commission_datum.update_entity(entity_detail)
        return entity_detail
    
    def _update_from_domain_service(self, entity_detail: EDetail) -> EDetail:
        if entity_detail.purchase_price.amount is None:
            ## List[EEc]が必要
            data = self.domain_service.compare_prices(entity_detail.product_id.value)
            entity_detail.ec_id(data['ec_id'])
            entity_detail.update_purchase_price(data['price'], 'JPY')
        return entity_detail
    
    def _update_from_entity_method(self, entity_detail: EDetail) -> EDetail:
        if entity_detail.import_fees.amount is None:
            import_fees = entity_detail.calc_import_fees()
            entity_detail.update_import_fees(import_fees, 'JPY')
        if entity_detail.roi.value is None:
            roi = entity_detail.calc_roi()
            entity_detail.update_roi(roi)
        return entity_detail