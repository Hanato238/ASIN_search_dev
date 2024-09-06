import mysql.connector as mydb
import keepa
import os
import dotenv

dotenv.load_dotenv()


class KeepaAPI:
    def __init__(self):
        self.api_key = os.getenv("KEEPA_API_KEY")
        self.api = keepa.Keepa(self.api_key)

    def search_asin_by_seller(self, seller):
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            return products[seller]['asinList']
        except Exception as e:
            print(f"Error fetching ASINs for seller {seller}: {e}")
            return []
        
    def get_product_details(self, asin):
        try:
            product = self.api.query(asin)[0]
            print(product)
            weight = product['packageWeight']
            if weight == 0 or weight == -1:
                weight=product['itemWeight']
            image_url = product['imagesCSV']
            amazon_url = f"https://www.amazon.co.jp/dp/{asin}"
            return weight, image_url, amazon_url
        except Exception as e:
            print(f"Error fetching details for ASIN {asin}: {e}")
            return None, None, None

        
def main():
    api = KeepaAPI()
    try:
        details = api.get_product_details('B095K3BV4G')
        print(details)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()