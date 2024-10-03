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
    detail_updater = keepa.detail_updater(db_client, keepa_client)

    sp_credentials = { 
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'lwa_app_id': os.getenv('LWA_APP_ID'),
        'lwa_client_secret': os.getenv('LWA_CLIENT_SECRET'),
        'marketplace': os.getenv('SP_API_DEFAULT_MARKETPLACE')
    }
    sp_api = sp_api_client.sp_api(**sp_credentials, database_client=db_client)

    searcher = vision.image_searcher(db_client)

    scraper = ec_scraper.get_scraper(db_client)

    calc = calculator.calculator(db_client)

    # record_products_master = {'id', 'asin', 'weight', 'weight_unit', 'image_url', 'last_search', 'is_good'}
    records_products_master = sp_api.get.get_product_to_process()

    if not records_products_master:
        print("No products to process")

    # record : products_master object
    # details = {'id', 'asin', 'weight', 'weight_unit', 'image_url'}
    # sales_rank_drops = {'asin', 'sales_rank_drops'}
    for record_product_master in records_products_master:
        # fill product_master {'weight', 'weight_unit', 'image_url'}
        record_product_master = sp_api.process_product_detail(record_product_master)

        #record_product_detail = {'id':'', 'asin_id':'', 'ec_url_id':'', 'product_price':'', 'research_date':'', 'three_month_sales':'', 'competitors':'', 'sales_price':'', 'commission':'', 'expected_import_fees':'', 'expected_roi':'', 'decision':'', 'final_dicision':''}
        record_product_detail = detail_updater.get_record_to_process(record_product_master)
        if len(record_product_detail) == 0:
            continue
        detail_updater.process_sales_rank_drops(record_product_detail[0])
        # fill product_detail {'competitors'}
        if record_product_detail['competitors'] == None:
            detail_updater.process_get_competitors(record_product_master)

        # fill product_detail {'ec_search'}
        # fill product_ec {'id', 'asin_id', 'ec_url'}
        monthly_sales_per_cart = record_product_detail['three_month_sales'] / record_product_detail['competitors']
        if record_product_detail['three_month_sales'] == 0 or record_product_detail['three_month_sales'] > 200 or monthly_sales_per_cart > 1:
            searcher.update.update_product_status(record_product_detail['id'])
        else:
            searcher.process_image_url(record)

        # fill prouct_ec {'price', 'currency', 'availability'}
        records_product_ec = scraper.get_ec_urls(record)
        for record in records_product_ec:
            scraper.scrape_and_save(record)

        # fill products_detail {'ec_url_id'} {'product_price'} {'sales_price'} {'commission'} {'expected_import_fees'}
        record_product_detail = calc.process_product_price(record_product_detail)
        record_product_detail = calc.process_sales_price(record_product_detail)
        record_product_detail = sp_api.process_commission(record_product_detail)
        record_product_detail = calc.process_expected_import_fees(record_product_master, record_product_detail)
        record_product_detail = calc.process_expected_roi(record_product_detail)
        record_product_detail = calc.process_product_decision(record_product_detail)

    db_client.close()

## not filled : products_master(last_search), products_detail(research_date, final_dicision)

## All filled : sellers, junction, products_master, products_ec, ec_sites

if __name__ == "__main__":
    main()
