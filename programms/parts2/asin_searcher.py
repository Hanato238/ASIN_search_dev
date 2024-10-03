import os
import dotenv

# for database client
import modules.database_client as db
# for keepa client
import modules.keepa_client as keepa

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

    keepa_api_key = os.getenv('KEEPA_API_KEY')
    keepa_client = keepa.keepa_client(keepa_api_key)
    manager = keepa.asin_searcher(db_client, keepa_client)

    try:
        manager.process_seller()
    except Exception as e:
        logging.info(f"Error processing seller: {e}")

    finally:
        db_client.close()

if __name__ == "__main__":
    main()
