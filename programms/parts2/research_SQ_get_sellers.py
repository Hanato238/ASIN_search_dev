import keepa
import os
import dotenv

import modules.database_client as db
import modules.keepa_client as keepa

dotenv.load_dotenv()


def main():
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }
    db_client = db.database_client(**db_config)

    keepa_api_key = os.getenv("KEEPA_API_KEY")
    keepa_client = keepa.keepa(keepa_api_key)
    searcher = keepa.seller_searcher(db_client, keepa_client)

    searcher.process_search_seller()

    db_client.close()

if __name__ == "__main__":
    main()