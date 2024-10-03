import os
import dotenv

# for KeepaClient
import modules.keepa_client as keepa

# for SpAPIClitne
import modules.amazon_api_client as sp_api_client

# for ImageSearcher
import modules.image_searcher as vision

# for database client
import modules.database_client as db

# for ec_site_scraper
import modules.ec_site_scraper as ec_scraper

# for calculator
import modules.calculator as calculator

import logging

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    db_client = db.database_client(**db_config)

    api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = keepa.keepa_client(api_key)
    detail_updater = keepa.detail_updater(db_client, keepa_client)

    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    sp_api = sp_api_client.sp_api(**sp_credentials, database_client=db_client)


    calc = calculator.calculator(db_client)

    records_products_detail = detail_updater.get_record_to_process()
    if len(records_products_detail) == 0:
        print("No products to process")
        return
    
    for record_products_detail in records_products_detail:    
        product_id = record_products_detail['id']

        try:
            if record_products_detail['three_month_sales'] is None:
                    record_products_detail = detail_updater.process_sales_rank_drops(record_products_detail)
        except Exception as e:
            logging.info(f"Error processing sales rank drops: {e}")
            continue


        try:
            if record_products_detail['competitors'] is None:
                record_products_detail = detail_updater.process_get_competitors(record_products_detail)
        except Exception as e:
            logging.info(f"Error processing competitors: {e}")
            continue
        

        try:
            if record_products_detail['product_price'] is None:
                record_products_detail = calc.process_product_price(record_products_detail)
        except Exception as e:
            logging.info(f"Error processing product price: {e}")
            continue

        try:
            if record_products_detail['sales_price'] is None:
                record_product_detail = sp_api.process_sales_price(record_product_detail)
        except Exception as e:
            logging.info(f"Error processing sales price: {e}")
            continue

        try:
            if record_products_detail['commission'] is None:
                record_product_detail = sp_api.process_commission(record_product_detail)
        except Exception as e:
            logging.info(f"Error processing commission: {e}")
            continue

        try:
            if record_product_detail['expected_import_fees'] is None:
                record_product_detail = calc.process_expected_import_fees(record_product_detail)
        except Exception as e:
            logging.info(f"Error processing expected import fees: {e}")
            continue

        try:
            if record_product_detail['expected_roi'] is None:
                record_product_detail = calc.process_expected_roi(record_product_detail)
        except Exception as e:
            logging.info(f"Error processing expected roi: {e}")
            continue

        try:
            record_product_detail = calc.process_product_decision(record_product_detail)
        except Exception as e:
            print(f"Error processing product {product_id}: {e}")
            continue

if __name__ == '__main__':
    main()