from typing import Any, Dict, Optional
import logging
from programms.parts3.domain.interface.i_repository import IRepoForSeller, IRepoForMaster, IRepoForJunction, IRepoForDetail, IRepoForEc
from programms.parts3.infrastructure.object.dto import SellerData, MasterData, JunctionData, DetailData, EcData
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

### Dict→Entityのコードが必要
### Entity→DTOのコードも

class RepoForSeller(IRepoForSeller):
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## upsert
    def save(self, seller: SellerData) -> None:
        query = """
            INSERT INTO sellers (seller, is_good)
            VALUES (%s, %s)
            ON DUPULICATE KEY UPDATE
            is_good = VALUES(is_good)"
        """
        data = (seller.seller.value, seller.is_good.value)
        self.db_client.execute_update(query, data)

## find by column
    def find_by_column(self, sellerid: Optional[str] = None, is_good: Optional[bool] = None) -> Dict[str, Any]:
        query = "SELECT * FROM sellers WHERE"
        params = []
        if sellerid is not None:
            query += " seller = %s"
            params.append(sellerid)
        if is_good is not None:
            query += " is_good = %s"
            params.append(is_good)
        result = self.db_client.execute_query(query, params)
        return result

class RepoForJunction(IRepoForJunction):
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## upsert
    def save(self, junction: JunctionData) -> None:
        query = """
            INSERT INTO junctions (seller_id, product_id)
            VALUES (%s, %s)
            ON DUPULICATE KEY UPDATE
            seller_id = VALUES(seller_id), product_id = VALUES(product_id)
        """
        data = (junction.seller_id, junction.product_id)
        self.db_client.execute_update(query, data)

## find by column
    def find_by_column(self, seller_id: Optional[int] = None, product_id: Optional[int] = None) -> Dict[str, Any]:
        query = "SELECT * FROM junctions WHERE"
        params = []
        if seller_id is not None:
            query += " seller_id = %s"
            params.append(seller_id)
        if product_id is not None:
            query += " product_id = %s"
            params.append(product_id)
        result = self.db_client.execute_query(query, params)
        return result

class RepoForMaster(IRepoForMaster):
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## upsert
    def save(self, product: MasterData) -> None:
        query = """
            INSERT INTO products_master (asin, weight, weight_unit, image_url, last_search, is_good, is_filled, ec_search)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPULICATE KEY UPDATE
            weight = VALUES(weight), weight_unit = VALUES(weight_unit), image_url = VALUES(image_url), last_search = VALUES(last_search), is_good = VALUES(is_good), is_filled = VALUES(is_filled), ec_search = VALUES(ec_search)
        """
        data = (product.asin, product.weight, product.weight_unit, product.image_url, product.last_search, product.is_good, product.is_filled, product.ec_search)
        self.db_client.execute_update(query, data)

## find by column
    def find_by_column(self, id: Optional[int] = None, asin: Optional[str] = None, weight: Optional[float] = None, unit: Optional[str] = None, image_url: Optional[str] = None, ec_search: Optional[bool] = None, is_good: Optional[bool] = None, is_filled: Optional[bool] = None) -> Dict[str, Any]:
        query = "SELECT * FROM products_master WHERE"
        params = []
        if id is not None:
            query += " id = %s"
            params.append(id)
        if asin is not None:
            query += " asin = %s"
            params.append(asin)
        if weight is not None:
            query += " weight = %s"
            params.append(weight)
        if unit is not None:
            query += " weight_unit = %s"
            params.append(unit)
        if image_url is not None:
            query += " image_url = %s"
            params.append(image_url)
        if ec_search is not None:
            query += " ec_search = %s"
            params.append(ec_search)
        if is_good is not None:
            query += " is_good = %s"
            params.append(is_good)
        if is_filled is not None:
            query += " is_filled = %s"
            params.append(is_filled)
        result = self.db_client.execute_query(query, params)
        return result


class RepoForDetail(IRepoForDetail):
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## upsert
    def save(self, product: DetailData) -> None:
        query = """
            INSERT INTO products_detail (product_id, ec_id, purchase_price, research_date, three_month_sales, competitors, sales_price, commission, import_fees, roi, decision, final_decision, is_filled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPULICATE KEY UPDATE
            """
        data = (product.product_id, product.ec_id, product.purchase_price, product.research_date, product.three_month_sales, product.competitors, product.sales_price, product.commission, product.import_fees, product.roi, product.decision, product.final_decision, product.is_filled)
        self.db_client.execute_update(query, data)

## find by column ## dateやfloatは等号ではなく、不等式へ
    def find_by_column(self, id: Optional[int] = None, product_id: Optional[int] = None, ec_id: Optional[int] = None, purchase_price: Optional[float] = None, research_date: Optional[datetime] = None, three_month_sales:Optional[int] = None, competitors: Optional[int] = None, import_fees: Optional[float] = None, roi: Optional[float] = None, decision: Optional[bool] = None, final_dicision: Optional[bool] = None, is_filled: Optional[bool] = None) -> Dict[str, Any]:
        query = "SELECT * FROM products_detail WHERE"
        params = []
        if id is not None:
            query += " id = %s"
            params.append(id)
        if product_id is not None:
            query += " product_id = %s"
            params.append(product_id)
        if ec_id is not None:
            query += " ec_id = %s"
            params.append(ec_id)
        if purchase_price is not None:
            query += " purchase_price = %s"
            params.append(purchase_price)
        if research_date is not None:
            query += " research_date = %s"
            params.append(research_date)
        if three_month_sales is not None:
            query += " three_month_sales = %s"
            params.append(three_month_sales)
        if competitors is not None:
            query += " competitors = %s"
            params.append(competitors)
        if import_fees is not None:
            query += " import_fees = %s"
            params.append(import_fees)
        if roi is not None:
            query += " roi = %s"
            params.append(roi)
        if decision is not None:
            query += " decision = %s"
            params.append(decision)
        if final_dicision is not None:
            query += " final_dicision = %s"
            params.append(final_dicision)
        if is_filled is not None:
            query += " is_filled = %s"
            params.append(is_filled)
        result = self.db_client.execute_query(query, params)
        return result
    


class RepoForEc(IRepoForEc):
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## upsert
    def save(self, ec_dto: EcData) -> None:
        query = """
            INSERT INTO products_ec (product_id, price, currency, is_available, ec_url, is_filled, is_supported)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPULICATE KEY UPDATE
            """
        data = (ec_dto.product_id, ec_dto.price, ec_dto.currency, ec_dto.is_available, ec_dto.ec_url, ec_dto.is_filled, ec_dto.is_supported)
        self.db_client.execute_update(query, data)

## find by column
    def find_by_column(self, id: Optional[int] = None, price: Optional[float] = None, is_available: Optional[bool] = None, ec_url: Optional[str] = None, is_filled: Optional[bool] = None, is_supported: Optional[bool] = None) -> Dict[str, Any]:
        query = "SELECT * FROM products_ec WHERE"
        params = []
        if id is not None:
            query += " id = %s"
            params.append(id)
        if price is not None:
            query += " price = %s"
            params.append(price)
        if is_available is not None:
            query += " is_available = %s"
            params.append(is_available)
        if ec_url is not None:
            query += " ec_url = %s"
            params.append(ec_url)
        if is_filled is not None:
            query += " is_filled = %s"
            params.append(is_filled)
        if is_supported is not None:
            query += " is_supported = %s"
            params.append(is_supported)
        result = self.db_client.execute_query(query, params)
        return result

## update
    def update_products_ec(self, record: Dict[str, Any]) -> None:
        product_id = record['product_id']
        ec_url = record['ec_url']
        query = "INSERT INTO products_ec (product_id, ec_url) VALUES (%s, %s)"
        self.db_client.execute_update(query, (product_id, ec_url))
        logging.info(f"Inserted new EC URL: {ec_url} for product_id {product_id}")
