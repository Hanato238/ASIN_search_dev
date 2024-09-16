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

    class RepositoryToSearchImage {
        -db
        +__init__(db_client)
        +get_positive_list()
        +get_products_to_process()
        +save_ec_url(product_id, ec_url)
        +update_product_status(product_id)
    }

    class ImageSearcher {
        -client
        +__init__()
        +search_image(image_url, positive_list)
    }

    class ImageSearchService {
        -repository_search_image
        -searcher
        +__init__(repository_search_image, searcher)
        +process_product(product, positive_list)
        +run()
    }

    DatabaseClient --> RepositoryToSearchImage : uses
    RepositoryToSearchImage --> ImageSearchService : uses
    ImageSearcher --> ImageSearchService : uses

```