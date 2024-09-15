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

    DatabaseClient --> AmazonProductUpdater : uses

```