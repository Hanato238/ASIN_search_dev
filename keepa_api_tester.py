import keepa
import os
import dotenv

dotenv.load_dotenv()

api_key = os.getenv('KEEPA_API_KEY')
api = keepa.Keepa(api_key)
asin = 'B08YHCZNC6'

products = api.query(asin, domain='JP', stats=90)
print(products[0]['offers'])