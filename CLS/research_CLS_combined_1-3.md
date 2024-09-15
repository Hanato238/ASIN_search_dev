```mermaid
classDiagram
    class DatabaseClient {
        -connection
        -cursor
        +__init__(host, user, password, database)
        +execute_query(query, params)
        +execute_update(query, params)
        +close()
    }

    class KeepaClient {
        -api
        +__init__(api_key)
        +search_asin_by_seller(seller)
        +query_seller_info(asin)
    }

    class SellerManager {
        -db_client
        -keepa_client
        +__init__(db_client, keepa_client)
        +get_sellers()
        +add_product_master(asin)
        +get_product_id(asin)
        +write_asin_to_junction(seller, product_id)
        +process_sellers()
    }

    class SellerSearcher {
        -db
        -api
        +__init__(db_client, keepa_client)
        +search_seller()
        +extract_info(data)
    }

    class AmazonProductUpdater {
        -credentials
        -marketplace
        -db
        +__init__(db, refresh_token, lwa_app_id, lwa_client_secret, marketplace)
        +fetch_products()
        +fetch_product_details(asin)
        +update_product(product_id, weight, weight_unit, image_url)
        +process_products()
    }

    class ImageSearcher {
        -client
        +__init__()
        +search_image(image_url, positive_list)
    }

    class ImageSearchService {
        -db
        -searcher
        +__init__(db_client)
        +get_positive_list()
        +process_product(product, positive_list)
        +run()
    }

    SellerManager --> DatabaseClient : uses
    SellerManager --> KeepaClient : uses
    SellerSearcher --> DatabaseClient : uses
    SellerSearcher --> KeepaClient : uses
    DatabaseClient --> AmazonProductUpdater : uses
    DatabaseClient --> ImageSearchService : uses
    ImageSearcher --> ImageSearchService : uses


```