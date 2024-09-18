import keepa
import dotenv
import os
import logging

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)

def test():
    api_key = os.getenv("KEEPA_API_KEY")
    api = keepa.Keepa(api_key)
    print(api.tokens_left)

test()