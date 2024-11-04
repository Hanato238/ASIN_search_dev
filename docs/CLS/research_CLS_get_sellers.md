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

    class RepositoryToGetSeller {
        -db
        +__init__(db_client)
        +get_all_products()
        +get_seller_count(seller)
        +add_seller(seller)
        +get_seller_id(seller)
        +add_junction(seller_id, product_id)
    }

    class KeepaClient {
        -api
        +__init__(api_key)
        +search_asin_by_seller(seller)
        +query_seller_info(asin)
    }

    class SellerSearcher {
        -repository
        -api
        +__init__(repository, keepa_client)
        +search_seller()
        +extract_info(data)
        +count_FBA_sellers(data)
    }

    DatabaseClient --> RepositoryToGetSeller : uses
    RepositoryToGetSeller --> SellerSearcher : uses
    KeepaClient --> SellerSearcher : uses

```