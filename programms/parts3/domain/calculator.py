import os
import dotenv
import yfinance as yf
import logging
from typing import Any, Dict, List, Tuple, Optional


dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class RepositoryToGet:
    def __init__(self, db_client: Any):
        self.db_client = db_client

    def get_purchase_prices(self, asin_id: str) -> List[Tuple[str, float, str]]:
        query = "SELECT id, price, price_unit FROM products_ec WHERE asin_id = %s"
        return self.db_client.execute_query(query, (asin_id,))
    
    # is_good=NULL or Trueのidをproducts_masterから取得
    def get_products_to_evaluate(self) -> List[Dict[str, int]]:
        query = "SELECT id FROM products_master WHERE is_good IS NULL OR is_good = TRUE"
        return self.db_client.execute_query(query)

    # asin_idの直近3件の判定を取得
    def get_decisions(self, product_id: int) -> List[Dict[int, bool]]:
        logging.info(f"Fetching decisions for product_id {product_id}")
        query = """
        SELECT decision FROM products_detail 
        WHERE asin_id = %s 
        ORDER BY id DESC 
        LIMIT 3
        """
        return self.db_client.execute_query(query, (product_id,))

    # is_good=NULL or Trueのidをsellersから取得
    def get_sellers_to_evaluate(self) -> List[Dict[str, int]]:
        logging.info("Fetching sellers to evaluate")
        query = "SELECT id FROM sellers WHERE is_good IS NULL OR is_good = TRUE"
        return self.db_client.execute_query(query)

    def get_seller_products(self, seller_id: str) -> List[Dict[str, int]]:
        logging.info(f"Fetching products for seller_id {seller_id}")
        query = """
        SELECT COUNT(*) as total, SUM(CASE WHEN pm.is_good = True THEN 1 ELSE 0 END) as num 
        FROM junction j JOIN products_master pm on j.product_id = pm.id 
        WHERE j.seller_id = %s
        """
        return self.db_client.execute_query(query, (seller_id,))
    
    def get_product_weight(self, asin_id: int) -> Dict[str, Any]:
        query = "SELECT weight, weight_unit FROM products_master WHERE id = %s"
        return self.db_client.execute_query(query, (asin_id,))
    
    def get_import_fees(self, asin_id: int) -> Dict[str, Any]:
        query = "SELECT import_fees FROM products_detail WHERE asin_id = %s AND import_fees IS NOT NULL"
        return self.db_client.execute_query(query, (asin_id,))

class RepositoryToUpdate:
    def __init__(self, db_client: Any):
        self.db_client = db_client

    def update_product_is_good(self, product_id: int) -> None:
        logging.info(f"Updating product is_good for product_id {product_id}")
        query = "UPDATE products_master SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (product_id,))

    def update_seller_is_good(self, seller_id: str) -> None:
        logging.info(f"Updating seller is_good for seller_id {seller_id}")
        query = "UPDATE sellers SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (seller_id,))

    def update_purchase_price(self, id: int, price: Dict[str, Any]) -> None:
        logging.info(f"Updating product price for id {id}")
        query = """
            UPDATE products_detail 
            SET ec_url_id = %s, purchase_price = %s
            WHERE id = %s"""
        self.db_client.execute_update(query, (price['id'], price['price_in_jpy'], id))

    def update_import_fees(self, id: int, price: float) -> None:
        logging.info(f"Updating expected import fees for id {id}")
        query = "UPDATE products_detail SET import_fees = %s WHERE id = %s"
        self.db_client.execute_update(query, (price, id))

    def update_roi(self, asin_id: int, roi: float) -> None:
        logging.info(f"Updating expected ROI for asin_id {asin_id}")
        query = "UPDATE products_detail SET roi = %s WHERE asin_id = %s AND roi IS NULL"
        self.db_client.execute_update(query, (roi, asin_id))

    def update_decision(self, record: Dict[str, Any], decision: bool) -> None:
        logging.info(f"Updating product decision for id {record['id']}")
        id = record['id']
        query = "UPDATE products_detail SET decision = %s WHERE id = %s"
        self.db_client.execute_update(query, (decision, id))



class EvaluateAsinAndSellers:
    def __init__(self, repository: RepositoryToGet):
        self.repository = repository
    
    def evaluate_purchase_price(self, prices: List[Tuple[str, float, str]]) -> Dict[str, Any]:
        logging.info("Evaluating product prices")
        min_price_in_jpy = float('inf')
        min_price_product = {'id': '', 'price_in_jpy': 0}
    
        for id, price, price_unit in prices:
            converter = CurrencyConverter(f'{price_unit}JPY=X')
            price_in_jpy = converter.convert_price(price)
        
            if price_in_jpy < min_price_in_jpy:
                min_price_in_jpy = price_in_jpy
                min_price_product = {'id': id, 'price_in_jpy': price_in_jpy}
    
        return min_price_product

    def evaluate_products(self) -> None:
        logging.info("Evaluating products")
        products = self.repository.get_products_to_evaluate()
        for product in products:
            decisions = self.repository.get_decisions(product['id'])
            if sum(d['decision'] for d in decisions) > 1:
                self.repository.update_product_is_good(product['id'])

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

class CurrencyConverter:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.exchange_rate = self.get_exchange_rate()

    def get_exchange_rate(self) -> float:
        data = yf.Ticker(self.ticker)
        exchange_rate = data.history(period="1d")['Close'][0]
        return exchange_rate

    def convert_price(self, price: float) -> float:
        logging.info(f"Converting price {price} to JPY at rate {self.exchange_rate}")
        return price * self.exchange_rate
    
class Calculator:
    def __init__(self, db_client: Any):
        self.get = RepositoryToGet(db_client)
        self.update = RepositoryToUpdate(db_client)

    def process_purchase_price(self, record: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"Processing product price for product id: {record['id']}")
        asin_id = record['asin_id']
        detail_id = record['id']
        prices = self.get.get_purchase_prices(asin_id)
        min_price_in_jpy = float('inf')
        min_price_product = {'id': '', 'price_in_jpy': 0}
    
        for id, price, price_unit in prices:
            converter = CurrencyConverter(f'{price_unit}JPY=X')
            price_in_jpy = converter.convert_price(price)
        
            if price_in_jpy < min_price_in_jpy:
                min_price_in_jpy = price_in_jpy
                min_price_product = {'id': id, 'price_in_jpy': price_in_jpy}
    
        purchase_prices = min_price_product
        self.update.update_purchase_price(detail_id, purchase_prices)
        record['purchase_price'] = purchase_prices['price_in_jpy']
        record['ec_url_id'] = purchase_prices['id']
        return record
    
    def process_import_fees(self, record_product_detail: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"Processing expected import fees for product id: {record_product_detail['id']}")
        import_tax = record_product_detail['purchase_price'] * 0.1
        weights = self.get.get_product_weight(record_product_detail['asin_id'])
        weight = weights['weight']
        weight_unit = weights['weight_unit']

        if weight_unit == 'kilograms':
            weight = weight*1000 # kilo/gram
        elif weight_unit == 'pounds':
            weight = weight*453.6 # pound/gram
        elif weight_unit == 'ounces':
            weight = weight*28.35 # ounce/gram
        elif weight_unit == 'grams':
            weight = weight
        else:
            raise ValueError('Invalid weight unit')
        
        import_fees = import_tax + weight * 2
        record_product_detail['import_fees'] = import_fees
        detail_id = record_product_detail['id']
        self.update.update_import_fees(detail_id, import_fees)
        logging.info(f"Expected import fees for product id {record_product_detail['id']}: {import_fees}")  
        return record_product_detail
    
    def process_roi(self, record: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"Processing expected ROI for product id: {record['id']}")
        sales_price = record['sales_price']
        purchase_price = record['purchase_price']
        commission = record['commission']
        import_fees = record['import_fees']
        roi = (sales_price - purchase_price - commission - import_fees) / purchase_price
        record['roi'] = roi
        self.update.update_roi(record['id'], roi)
        self.update.update_decision(record['id'], roi)
        logging.info(f"Update xpected ROI for product id {record['id']}: {roi}")
        return record
    
    def process_decision(self, record: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"Processing product decision for product id: {record['id']}")
        if record['roi'] > 0.3 and record['three_month_sales']/record['competitors'] > 3 and record['three_month_sales'] < 100:
            decision = 1
        else:
            decision = 0
        self.update.update_decision(record, decision)
        logging.info(f"Product decision for product id {record['id']}: {decision}")
        return record

    def evaluate_products(self) -> None:
        logging.info("Evaluating products")
        products = self.repository.get_products_to_evaluate()
        for product in products:
            decisions = self.repository.get_decisions(product['id'])
            if sum(d['decision'] for d in decisions) > 1:
                self.repository.update_product_is_good(product['id'])
        logging.info("Products evaluated")

    def evaluate_sellers(self) -> None:
        logging.info("Evaluating sellers")
        sellers = self.repository.get_sellers_to_evaluate()
        for seller in sellers:
            result = self.repository.get_seller_products(seller['id'])
            if result[0]['total'] == 0:
                continue
            p = result[0]['num'] / result[0]['total'] 
            if p > 0.3:
                self.repository.update_seller_is_good(seller['id'])
        logging.info("Sellers evaluated")


def calculator(db_client: Any) -> Calculator:
    return Calculator(db_client)