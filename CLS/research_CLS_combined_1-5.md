```mermaid
classDiagram

    namespace DB {
        class DatabaseClient {
            -_instance: DatabaseClient
            -connection: mysql.connector.connection
            -cursor: mysql.connector.cursor
            -initialized: bool
            +__new__(cls, *args, **kwargs)
            +__init__(host: str, user: str, password: str,  database: str)
            +execute_query(query: str, params: Optional[Dict[str,   Any]]) List[Dict[str, Any]]
            +execute_update(query: str, params: Optional[Dict[str,  Any]]) void
            +close() void
        }
    }

    namespace keepa{
        class KeepaClient {
            - Keepa api
            - static KeepaClient _instance
            + KeepaClient __new__(cls, api_key: str)
            + void _initialize(api_key: str)
            + List~str~ search_asin_by_seller(seller: str)
            + Dict~str, Any~ query_seller_info(asin: str)
            + int get_sales_rank_drops(asin: str)
        }

        class SellerSearcher {
            - RepositoryToGetSeller repository
            - KeepaClient api
            + SellerSearcher(database_client: Any, keepa_client:    Any)
            + void process_search_seller()
            + List~Dict~ extract_info(data: List~Dict~)
            + int count_FBA_sellers(data: List~Dict~)
        }   
        
        class AsinSearcher {
            - RepositoryToGetAsin repository
            - KeepaClient keepa_client
            + AsinSearcher(db_client: Any, keepa_client: Any)
            + void process_seller()
        }

        class DetailUpdater {
            - RepositoryToGetSalesToGet get
            - RepositoryToGetSalesToUpdate update
            - KeepaClient keepa_client
            + DetailUpdater(db_client: Any, keepa_client: Any)
            + List~Dict~ get_record_to_process()
            + void update_detail_status(record: Dict~str, Any~)
            + Optional~Dict~ process_sales_rank_drops(record: Dict~str, Any~)
            + Optional~Dict~ process_get_competitors(record: Dict~str, Any~)
            + List~Dict~ extract_info(data: List~Dict~)
            + int count_FBA_sellers(data: List~Dict~)
        }
    }
    AsinSearcher --> KeepaClient : uses
    SellerSearcher --> KeepaClient : uses
    DetailUpdater --> KeepaClient : uses

    namespace imageSearch{
        class ImageSearcher {
            +__init__()
            +search_image(image_url: str, positive_list: Optional[List[str]]): Optional[List[str]]
        }
        class ImageSearchService {
            +__init__(database_client: Any)
            +get_products_to_process(): List[Dict[str, Any]]
            +process_image_url(record: Dict[str, Any])
        }
    }
    ImageSearchService --> ImageSearcher : uses

    namespace spapi{
        class AmazonAPIClient {
            -credentials: dict
            -marketplace: str
            +__init__(refresh_token: str, lwa_app_id: str,  lwa_client_secret: str, marketplace: str)
            +request_product_details(result: Dict[str, Any]) Dict[str, Any]
            +request_product_price(asin: str) float
            +request_product_fees(asin: str, price: float) float
        }

        class AmazonFacade {
            -api_client: AmazonAPIClient
            -get: RepositoryToGet
            -update: RepositoryToUpdate
            +__init__(refresh_token: str, lwa_app_id: str, lwa_client_secret: str, marketplace: str, database_client: Any)
            +get_product_to_process() List[Dict[str, Any]]
            +process_product_detail(record_product_master: Dict[str, Any]) Dict[str, Any]
            +process_sales_price(record: Dict[str, Any]) Dict[str,  Any]
            +process_commission(record: Dict[str, Any]) Dict[str, Any]
        }
    }
    AmazonFacade --> AmazonAPIClient : uses

    namespace scraper{
        class BrightDataAPI {
            - dataset_id: str
            - api_key: str
            + __init__(dataset_id: str)
            + get_snapshot_id(url: str, dataset_name: str): str
            + get_detail(snapshot_id: str, max_retries: int=5): Union[Dict[str, Any], List[Dict[str, Any]]]
        }

        class AmazonScraper {
            - pattern: Pattern
            + __init__(dataset_id: str)
            + scrape_data(scraper: Any, url: str): Dict[str, Any]
        }

        class WalmartScraper {
            - pattern: Pattern
            + __init__(dataset_id: str)
            + scrape_data(scraper: Any, url: str): Dict[str, Any]
        }

        class EBayScraper {
            - pattern: Pattern
            + __init__(dataset_id: str)
            + scrape_data(scraper: Any, url: str): Dict[str, Any]
        }

        class ScraperFactory {
            + create_scraper(scraper_type: str, dataset_id: str):   BrightDataAPI
        }

        class ScraperFacade {
        - get: RepositoryToGet
        - update: RepositoryToUpdate
        + __init__(database_client: Any)
        + get_products_to_process(): List[Dict[str, Any]]
        + process_scrape(record: Dict[str, Any]): None
        + get_ec_site_and_dataset_id(url: str): Tuple[str, str]
        + create_scraper(ec_site: str, dataset_id: str): Any
        + update_record_with_scraped_data(record: Dict[str, Any], data_scraped: Dict[str, Any]): None
        + scrape_and_save(record: Dict[str, Any]): None
        }
    }

    BrightDataAPI <|-- AmazonScraper
    BrightDataAPI <|-- WalmartScraper
    BrightDataAPI <|-- EBayScraper
    ScraperFactory --> BrightDataAPI
    ScraperFacade --> ScraperFactory

    namespase calculator{
        class EvaluateAsinAndSellers {
            +__init__(repository: RepositoryToGet)
            +evaluate_product_price(prices: List[Tuple[str, float, str]]): Dict[str, Any]
            +evaluate_products(): None
            +evaluate_sellers(): None
        }

        class CurrencyConverter {
            +__init__(ticker: str)
            +get_exchange_rate(): float
            +convert_price(price: float): float
        }

        class Calculator {
            +__init__(db_client: Any)
            +process_product_price(record: Dict[str, Any]): Dict[str, Any]
            +process_expected_import_fees(record_product_detail: Dict[str, Any]): Dict[str, Any]
        }
    }
    EvaluateAsinAndSellers --> RepositoryToGet : uses
    Calculator --> RepositoryToGet : uses
    Calculator --> RepositoryToUpdate : uses
    EvaluateAsinAndSellers --> CurrencyConverter : uses
    Calculator --> CurrencyConverter : uses





    class RepositoryForSpAPI {
        -db_client
        +__init__(db_client)
        +fetch_products()
        +update_product(product_id, weight, weight_unit, image_url)
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

    class RepositoryToSearchImage {
        -db
        +__init__(db_client)
        +get_positive_list()
        +get_products_to_process()
        +save_ec_url(product_id, ec_url)
        +update_product_status(product_id)
    }

    class RepositoryToGetSales {
        -db_client
        +__init__(db_client)
        +get_asins_without_sales_rank()
        +update_sales_rank(asin, sales_rank_drops)
    }

    class AmazonAPIClient {
        -credentials
        -marketplace
        +__init__(refresh_token, lwa_app_id, lwa_client_secret, marketplace)
        +fetch_product_details(asin)
    }

    class ImageSearcher {
        -client
        +__init__()
        +search_image(image_url, positive_list)
    }

    class AsinSearcher {
        -db_client
        -keepa_client
        +__init__(db_client, keepa_client)
        +process_sellers()
    }

    class AmazonProductUpdater {
        -db
        -api
        +__init__(db_client, api_client)
        +process_products()
    }

    class SellerSearcher {
        -repository
        -api
        +__init__(repository, keepa_client)
        +search_seller()
        +extract_info(data)
        +count_FBA_sellers(data)
    }

    class ImageSearchService {
        -repository_search_image
        -searcher
        +__init__(repository_search_image, searcher)
        +process_product(product, positive_list)
        +run()
    }

    class SalesRankUpdater {
        -db_client
        +keepa_client
        +__init__(db_client, keepa_client)
        +update_sales_ranks()
    }


```