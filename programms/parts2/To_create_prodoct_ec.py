import os
import dotenv

# for ImageSearcher
import modules.image_searcher as vision

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

    searcher = vision.image_searcher(db_client)

    records_products_master = searcher.get_products_to_process()
    if len(records_products_master) == 0:
        logging.info("No products to process")
    
    for record_products_master in records_products_master:
        if record_products_master['ec_search'] == None or record_products_master['ec_search'] == False:
            try:
                searcher.process_image_url(record_products_master)
            except Exception as e:
                logging.info(f"Error processing image url: {e}")
                continue

if __name__ == '__main__':
    main()