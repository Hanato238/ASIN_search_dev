import os
import dotenv
import time

import mysql.connector

dotenv.load_dotenv()

class DatabaseClient:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor(dictionary=True)
        print("connected to DB")

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

class RepositoryForEvaluation:
    def __init__(self, db_client):
        self.db_client = db_client

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
        
    def update_seller_is_good(self, seller_id):
        query = "UPDATE sellers SET is_good = 1 WHERE id = %s"
        self.db_client.execute_update(query, (seller_id,))

class EvaluateAsinAndSellers:
    def __init__(self, repository):
        self.repository = repository

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

def main():    
    db_client = DatabaseClient(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )
    repository = RepositoryForEvaluation(db_client)
    judge = EvaluateAsinAndSellers(repository)
    judge.evaluate_sellers()

if __name__ == "__main__":
    main()
