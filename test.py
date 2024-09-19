import time
import dotenv
import os
from sp_api.api import ListingsItems
import mysql.connector
from sp_api.base.exceptions import SellingApiRequestThrottledException

dotenv.load_dotenv()

class AmazonAPIClient:
    def __init__(self, refresh_token, lwa_app_id, lwa_client_secret, marketplace):
        self.credentials = {
            'refresh_token': refresh_token,
            'lwa_app_id': lwa_app_id,
            'lwa_client_secret': lwa_client_secret
        }
        self.marketplace = marketplace

def main():
    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    AmazonAPIClient(**sp_credentials)
    list = ListingsItems.get_listings_item(sellerId='A3UER180TVRC81')
    print(list)

if __name__ == '__main__':
    main()