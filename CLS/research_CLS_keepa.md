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

    class RepositoryToGetSales {
        -db_client
        +__init__(db_client)
        +get_asins_without_sales_rank()
        +update_sales_rank(asin, sales_rank_drops)
    }

    class KeepaClient {
        -api
        +__init__(api_key)
        +get_sales_rank_drops(asin)
    }

    class SalesRankUpdater {
        -db_client
        +keepa_client
        +__init__(db_client, keepa_client)
        +update_sales_ranks()
    }

    DatabaseClient --> RepositoryToGetSales : uses
    RepositoryToGetSales --> SalesRankUpdater : uses
    KeepaClient --> SalesRankUpdater : uses

```