import os
import dotenv
import time

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
    keepa_client = keepa.keepa_client(api_key)
    sales_rank_updater = keepa.sales_rank_updater(keepa.repository_to_get_sales(db_client), keepa_client)

    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    sp_api = sp_api_client.sp_api(**sp_credentials, database_client=db_client)

    searcher = vision.image_searcher()
    service = vision.image_search_service(vision.repository_to_search_image(db_client), searcher)

    scraper = ec_scraper.get_scraper()

    calc = calculator.calculator(db_client)

    products = sp_api.fetch_product_details()
    if not products:
        print("No products to process")

    # product = {'id', 'asin', 'image_url'}
    # details = {'id', 'asin', 'weight', 'weight_unit', 'image_url'}
    # sales_rank_drops = {'asin', 'sales_rank_drops'}
    for product in products:
        details = sp_api.fetch_product_details(product)
        sales_rank_drops = sales_rank_updater.get_sales_rank(details['asin'])
        sales_rank_updater.update_sales_rank(sales_rank_drops['asin'], sales_rank_drops['sales_rank_drops'])
        if sales_rank_drops['sales_rank_drops'] == 0 or sales_rank_drops['sales_rank_drops'] > 200:
            vision.repository_to_search_image.update_product_status(details['id'])
        else:
            service.process_product(details)

        ec_urls = scraper.get_ec_urls(details['id'])
        for ec_url in ec_urls:
            scraper.scrape_and_save(ec_url)

        # fill products_detail(product_price)
        product_price = calc.update_product_prices(details['id'])


        # fill products_detail(commission)
        sp_api.update_product_price(details['id'], product_price)
        # fill products_detail(expected_import_fees)
        calc.update_expected_import_fees(details['id'])
        #fill products_detail(expected_roi)
        calc.update_expected_roi(details['id'])
        # fill products_detail(dicision)
        calc.update_product_dicision(details['id'])


        # all_details = calc.get_all_details(details['asin'])
        # calc.calc_all_details(all_details)  

    db_client.close()

## not filled : products_detail(ec_url?id, product_price, monthly, decision)

## All filled : sellers, junction, products_master, products_ec, ec_sites

if __name__ == "__main__":
    main()
