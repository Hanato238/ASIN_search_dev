import os
import dotenv
import yfinance as yf
import logging
from typing import Any, Dict, List, Tuple, Optional


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
