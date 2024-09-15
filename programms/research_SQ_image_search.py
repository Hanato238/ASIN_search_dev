import os
from dotenv import load_dotenv
import mysql.connector
from google.cloud import vision

# 環境変数をロード
load_dotenv()

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

class ImageSearcher:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        # positive list + negative list方式にする? : positive list方式 + salvage方式にする
    
    def search_image(self, image_url, positive_list=None):
        image = vision.Image()
        image.source.image_uri = image_url    

        response = self.client.web_detection(image=image)
        annotations = response.web_detection

        if annotations.pages_with_matching_images:
            for page in annotations.pages_with_matching_images:
                if any(domain in page.url for domain in positive_list):
                    print(page.url)
                    return page.url
        return None

class ImageSearchService:
    def __init__(self, db_client):
        self.db = db_client
        self.searcher = ImageSearcher()
    
    # 画像検索を行う対象のECサイトリストを取得
    def get_positive_list(self):
        query = "SELECT ec_site FROM ec_sites WHERE to_research = TRUE"
        positive_list = [item['ec_site'] for item in self.db.execute_query(query)]
        return positive_list
    
    def process_product(self, product, positive_list):
        product_id = product['id']
        image_url = product['image_url']
        print(f'Processing product_id: {product_id}, image_url: {image_url}')

        # 画像検索でURLを取得
        ec_url = self.searcher.search_image(image_url, positive_list)
        print(f'Found ec_url: {ec_url}')
        
        # 得られたec_urlをDBに保存
        if ec_url:
            query = "SELECT * FROM products_ec WHERE asin_id = %s AND ec_url = %s"
            if not self.db.execute_query(query, (product_id, ec_url)):
                insert_query = "INSERT INTO products_ec (asin_id, ec_url) VALUES (%s, %s)"
                self.db.execute_update(insert_query, (product_id, ec_url))
            else:
                print("URL already exists in the database")

            # products_masterテーブルを更新
            update_query = "UPDATE products_master SET ec_search = TRUE WHERE id = %s"
            self.db.execute_update(update_query, (product_id,))
        else:
            print("No matching URL found")    

    def run(self):
        targets = self.db.execute_query("SELECT id, image_url FROM products_master WHERE ec_search IS NULL AND image_url IS NOT NULL")
        if len(targets) == 0:
            print("No products to process")
            return
        positive_list = self.get_positive_list()
        for product in targets:
            self.process_product(product, positive_list)

def main():
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }
    db_client = DatabaseClient(**db_config)
    service = ImageSearchService(db_client)
    service.run()
    db_client.close()

if __name__ == "__main__":
    main()
