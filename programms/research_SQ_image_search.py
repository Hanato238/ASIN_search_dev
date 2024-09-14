import os
from dotenv import load_dotenv
import mysql.connector
from google.cloud import vision

# 環境変数をロード
load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.database = os.getenv('DB_NAME')

    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def get_image_urls(self):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, image FROM products_master WHERE ec_search IS NULL")
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    def update_ec_url(self, product_id, ec_url):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE products_ec SET ec_url = %s, is_checked = TRUE WHERE asin_id = %s", (ec_url, product_id))
        connection.commit()
        cursor.close()
        connection.close()

class ImageSearcher:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        self.search_urls = ['https://www.amazon.com/', 'https://www.amazon.co.uk/', 'https://www.walmart.com/', 'https://www.1688.com/']

    def search_image(self, image_url):
        image = vision.Image()
        image.source.image_uri = image_url

        response = self.client.web_detection(image=image)
        annotations = response.web_detection

        if annotations.pages_with_matching_images:
            for page in annotations.pages_with_matching_images:
                if any(domain in page.url for domain in self.search_urls):
                    print(page.url)
                    #return page.url
        return None

class ImageSearchService:
    def __init__(self):
        self.db = Database()
        self.searcher = ImageSearcher()

    def run(self):
        image_urls = self.db.get_image_urls()
        for product_id, image_url in image_urls:
            print(f'product_id: {product_id}, image_url: {image_url}')
            ec_url = self.searcher.search_image(image_url)
            print(f'ec_url: {ec_url}')
            if ec_url:
                self.db.update_ec_url(product_id, ec_url)


def main(event, context):
    service = ImageSearchService()
    service.run()
'''

def main(event, context):
    test_image_url = "https://m.media-amazon.com/images/I/81SZekrUnEL.jpg"  # テスト用の画像URL
    service = ImageSearchService()
    ec_url = service.searcher.search_image(test_image_url)
    if ec_url:
        print(f"Found EC URL: {ec_url}")
    else:
        print("No EC URL found.")
'''

if __name__ == "__main__":
    main(None, None)
