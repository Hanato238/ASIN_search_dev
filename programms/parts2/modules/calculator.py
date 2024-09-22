import os
import dotenv
import yfinance as yf

dotenv.load_dotenv()

class RespositoryForCalc:
    def __init__(self, db_client):
        self.db_client = db_client

    def get_product_prices(self, asin_id):
        query = "SELECT id, price, price_unit FROM products_ec WHERE asin_id = %s"
        return self.db_client.execute_query(query, (asin_id,))

    def update_product_price(self, asin_id, product_price):
        query = "UPDATE products_master SET product_price = %s WHERE asin_id = %s"
        self.db_client.execute_update(query, (product_price, asin_id))
    
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

    def update_product_is_good(self, product_id):
        query = "UPDATE products_master SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (product_id,))

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
        
    def update_seller_is_good(self, seller_id):
        query = "UPDATE sellers SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (seller_id,))

    def update_product_price(self, asin_id, price):
        query = "UPDATE products_detail SET product_price = %s WHERE asin_id = %s"
        self.db_client.execute_update(query, (price, asin_id))

    def update_expected_import_fees(self, asin_id, price):
        query = "UPDATE products_detail SET expected_import_fees = %s WHERE asin_id = %s"
        self.db_client.execute_update(query, (price, asin_id))

    def update_expected_roi(self, asin_id, roi):
        query = "UPDATE products_detail SET expected_roi = %s WHERE asin_id = %s AND expected_roi IS NULL"
        self.db_client.execute_update(query, (roi, asin_id))

    def update_product_decision(self, asin_id, roi):
        if roi > 0.2:
            decision = 1
        else:
            decision = 0
        query = "UPDATE products_detail SET decision = %s WHERE asin_id = %s"
        self.db_client.execute_update(query, (decision, asin_id))

class EvaluateAsinAndSellers:
    def __init__(self, repository):
        self.repository = repository
    
    def get_product_price(self, prices):
        prices_in_jpy = []
        for price, price_unit in prices:
            converter = CurrencyConverter(f'{price_unit}JPY=X')
            price_in_jpy = converter.convert_price(price)
            prices_in_jpy.append(price_in_jpy)
        return min(prices_in_jpy)

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
        self.repository = RespositoryForCalc(db_client)
        self.evaluator = EvaluateAsinAndSellers(self.repository)

    def update_product_price(self, asin_id):
        prices = self.repository.get_product_prices(asin_id)
        product_price = self.evaluator.get_product_price(prices)
        self.repository.update_product_price(asin_id, product_price)
        return product_price
    
    def update_expected_import_fees(self, asin_id):
        import_tax = self.repository.get_product_prices(asin_id)*2
        weights = self.repository.get_product_weight(asin_id)
        for weight, weight_unit in weights:
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
        self.repository.update_expected_import_fees(asin_id, expected_import_fees)
        return expected_import_fees
    
    def update_expected_roi(self, asin_id):
        product_price = self.repository.get_product_prices(asin_id)
        expected_import_fees = self.repository.get_expected_import_fees(asin_id)
        roi = (expected_import_fees - product_price) / product_price
        self.repository.update_expected_roi(asin_id, roi)
        return roi