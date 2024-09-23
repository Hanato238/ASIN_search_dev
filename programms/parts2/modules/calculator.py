import os
import dotenv
import yfinance as yf

dotenv.load_dotenv()



class RepositoryToGet:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_product_prices(self, asin_id):
        query = "SELECT id, price, price_unit FROM products_ec WHERE asin_id = %s"
        return self.db_client.execute_query(query, (asin_id,))
    
    # is_good=NULL or Trueのidをproducts_masterから取得
    def get_products_to_evaluate(self):
        query = "SELECT id FROM products_master WHERE is_good IS NULL OR is_good = TRUE"
        return self.db_client.execute_query(query)

    # asin_idの直近3件の判定を取得
    def get_product_decisions(self, product_id):
        query = """
        SELECT decision FROM products_detail 
        WHERE asin_id = %s 
        ORDER BY id DESC 
        LIMIT 3
        """
        return self.db_client.execute_query(query, (product_id,))

    # is_good=NULL or Trueのidをsellersから取得
    def get_sellers_to_evaluate(self):
        query = "SELECT id FROM sellers WHERE is_good IS NULL OR is_good = TRUE"
        return self.db_client.execute_query(query)

    def get_seller_products(self, seller_id):
        query = """
        SELECT COUNT(*) as total, SUM(CASE WHEN pm.is_good = True THEN 1 ELSE 0 END) as num 
        FROM junction j JOIN products_master pm on j.product_id = pm.id 
        WHERE j.seller_id = %s
        """
        return self.db_client.execute_query(query, (seller_id,))
    
    def get_product_weight(self, asin_id):
        query = "SELECT weight, weight_unit FROM products_master WHERE asin_id = %s"
        return self.db_client.execute_query(query, (asin_id,))
    
    def get_expected_import_fees(self, asin_id):
        query = "SELECT expected_import_fees FROM products_detail WHERE asin_id = %s AND expected_import_fees IS NOT NULL"
        return self.db_client.execute_query(query, (asin_id,))

class RepositoryToUpdate:
    def __init__(self, db_client):
        self.db_client = db_client

    def update_product_is_good(self, product_id):
        query = "UPDATE products_master SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (product_id,))

    def update_seller_is_good(self, seller_id):
        query = "UPDATE sellers SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (seller_id,))

    def update_product_price(self, id, price):
        query = """
            UPDATE products_detail 
            SET ec_url_id = %s, product_price = %s
            WHERE id = %s"""
        self.db_client.execute_update(query, (price['id'], price['price_in_jpy'], id))

    def update_expected_import_fees(self, id, price):
        query = "UPDATE products_detail SET expected_import_fees = %s WHERE id = %s"
        self.db_client.execute_update(query, (price, id))

    def update_expected_roi(self, asin_id, roi):
        query = "UPDATE products_detail SET expected_roi = %s WHERE asin_id = %s AND expected_roi IS NULL"
        self.db_client.execute_update(query, (roi, asin_id))

    def update_product_decision(self, record, decision):
        id = record['id']
        query = "UPDATE products_detail SET decision = %s WHERE id = %s"
        self.db_client.execute_update(query, (decision, id))



class EvaluateAsinAndSellers:
    def __init__(self, repository):
        self.repository = repository
    
def evaluate_product_price(self, prices):
    min_price_in_jpy = float('inf')
    min_price_product = {'id': '', 'price_in_jpy': 0}
    
    for id, price, price_unit in prices:
        converter = CurrencyConverter(f'{price_unit}JPY=X')
        price_in_jpy = converter.convert_price(price)
        
        if price_in_jpy < min_price_in_jpy:
            min_price_in_jpy = price_in_jpy
            min_price_product = {'id': id, 'price_in_jpy': price_in_jpy}
    
    return min_price_product

    def evaluate_products(self):
        products = self.repository.get_products_to_evaluate()
        for product in products:
            decisions = self.repository.get_product_decisions(product['id'])
            if sum(d['decision'] for d in decisions) > 1:
                self.repository.update_product_is_good(product['id'])

    def evaluate_sellers(self):
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
    def __init__(self, ticker):
        self.ticker = ticker
        self.exchange_rate = self.get_exchange_rate()

    def get_exchange_rate(self):
        data = yf.Ticker(self.ticker)
        exchange_rate = data.history(period="1d")['Close'][0]
        return exchange_rate

    def convert_price(self, price):
        return price * self.exchange_rate
    
class Calculator:
    def __init__(self, db_client):
        self.evaluator = EvaluateAsinAndSellers(self.repository)
        self.get = RepositoryToGet(db_client)
        self.update = RepositoryToUpdate(db_client)

    def process_product_price(self, record):
        asin_id = record['asin_id']
        detail_id = record['id']
        prices = self.get.get_product_prices(asin_id)
        product_prices = self.evaluator.evaluate_product_price(prices)
        self.update.update_product_price(detail_id, product_prices)
        record['product_price'] = product_prices['price_in_jpy']
        record['ec_url_id'] = product_prices['id']
        return record
    
    def process_expected_import_fees(self, record_product_master, record_product_detail):
        import_tax = record_product_detail['product_price'] * 0.1
        weight = record_product_master['weight']
        weight_unit = record_product_master['weight_unit']

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
        
        expected_import_fees = import_tax + weight * 2
        record_product_detail['expected_import_fees'] = expected_import_fees
        detail_id = record_product_master['id']
        self.update.update_expected_import_fees(detail_id, expected_import_fees)
        return record_product_detail
    
    def process_expected_roi(self, record):
        sales_price = record['sales_price']
        product_price = record['product_price']
        commission = record['commission']
        expected_import_fees = record['expected_import_fees']
        roi = (sales_price - product_price - commission - expected_import_fees) / sales_price
        record['expected_roi'] = roi
        self.update.update_expected_roi(record['id'], roi)
        self.update.update_product_decision(record['id'], roi)
        return record
    
    def process_product_decision(self, record):
        if record['expected_roi'] > 0.3:
            decision = 1
        else:
            decision = 0
        self.update.update_product_decision(record, decision)
        return record
        