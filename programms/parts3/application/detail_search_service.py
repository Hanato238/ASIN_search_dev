from programms.parts3.domain.interface.i_api_client import IKeepaClient, IAmazonAPIClient, IImageSearcher, IScraper
from programms.parts3.domain.interface.i_repository import IRepoForMaster, IRepoForEc
from programms.parts3.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.parts3.domain.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData
from programms.parts3.domain.domain_service import DomainService, CalculateService

class DetailSearchService:
    def __init__(self, keepa_client: IKeepaClient, sp_api_client: IAmazonAPIClient, repo_master: IRepoForMaster) -> None:
        self.keepa_client = keepa_client
        self.sp_api_client = sp_api_client
        self.repository.master = repo_master
        self.domain_service = DomainService()
        self.calculate_service = CalculateService()

    def search_detail(self) -> None:
        dtos = self.domain_service.get_products_to_fill_detail()
        # dto: DetailData
        try:
        for dto in dtos:
            # commandクラス作る？
            # 利用APIごとにserviceクラスを分割
            if dto.three_month_sales is None:
                # dto.asinが欲しい
                dto.three_month_sales = self.keepa_client.get_three_month_sales(dto.asin)
        
            if dto.competitors is None:
                dto.competitors = self.keepa_client.get_competitors(dto.asin)
            

            if dto.commission is None:
                dto.commission = self.sp_api_client.request_product_fees(dto.asin)
            
            if dto.sales_price is None:
                dto.sales_price = self.sp_api_client.request_product_price(dto.asin)

            if dto.purchase_price is None:
                dto.purchase_price, dto.ec_id = self.calculate_service.compare_product_price(dto.product_id)

            if dto.import_fees is None:
                dto.import_fees = self.calculate_service.calculate_import_fees(dto.purchase_price)