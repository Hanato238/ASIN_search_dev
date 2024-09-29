import os
import dotenv

# for SpAPIClitne
import modules.amazon_api_client as sp_api_client

# for database client
import modules.database_client as db


dotenv.load_dotenv()


def main():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = db.database_client(**db_config)

    api_key = os.getenv('KEEPA_API_KEY')

    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    sp_api = sp_api_client.sp_api(**sp_credentials, database_client=db_client)

    # record_products_master = {'id', 'asin', 'weight', 'weight_unit', 'image_url', 'last_search', 'is_good'}
    records_products_master = sp_api.get.get_product_to_process()

    if not records_products_master:
        print("No products to process")

    # record : products_master object
    for record_product_master in records_products_master:
        # fill product_master {'weight', 'weight_unit', 'image_url'}
        try:
            record_product_master = sp_api.process_product_detail(record_product_master)
        except Exception as e:
            print(f"Error processing product detail: {e}")
            continue
    db_client.close()

if __name__ == '__main__':
    main()