import mysql.connector
import keepa
import time

# MySQLデータベースに接続
db = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword",
    database="yourdatabase"
)

cursor = db.cursor()

# Keepa APIキー
keepa_api_key = 'YOUR_KEEPA_API_KEY'
api = keepa.Keepa(keepa_api_key)

def get_seller_ids():
    cursor.execute("SELECT id FROM sellers")
    return cursor.fetchall()

def search_asin_by_seller(seller_id):
    try:
        products = api.query(seller_id, domain='JP', product_code_is_asin=False)
        return [product['asin'] for product in products]
    except Exception as e:
        print(f"Error fetching ASINs for seller {seller_id}: {e}")
        return []

def write_asin_to_db(seller_id, asin):
    try:
        cursor.execute("INSERT INTO junction (seller_id, asin, evaluate, product_master, created_at) VALUES (%s, %s, %s, %s, NOW())",
                       (seller_id, asin, False, True))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def main():
    while True:
        seller_ids = get_seller_ids()
        for seller_id in seller_ids:
            asins = search_asin_by_seller(seller_id[0])
            for asin in asins:
                write_asin_to_db(seller_id[0], asin)
        time.sleep(86400)  # 24時間ごとに実行

if __name__ == "__main__":
    main()
