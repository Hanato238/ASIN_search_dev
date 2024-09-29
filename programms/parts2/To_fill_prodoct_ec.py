import os
import dotenv

# for Scraping
import modules.ec_site_scraper as ec_scraper

# for database client
import modules.database_client as db

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

    scraper = ec_scraper.get_scraper(db_client)

    records_products_ec = scraper.get_products_to_process()
    if len(records_products_ec) == 0:
        logging.info("No products to process")
    
    for record_products_ec in records_products_ec:
        try:
            scraper.process_scrape(record_products_ec)
        except Exception as e:
            logging.info(f"Error processing image url: {e}")
            continue

if __name__ == '__main__':
    main()