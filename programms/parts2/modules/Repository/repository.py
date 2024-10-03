from typing import Any, Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class RepositoryForSellers:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client
## create
    def create_new_seller(self, seller: str) -> None:
        count = len(self.get_seller_from_sellerId(seller))
        if count > 0:
            logging.info(f"Seller {seller} already exists")
            return
        query = "INSERT INTO sellers (seller) VALUES (%s)"
        self.db_client.execute_update(query, (seller,))
        logging.info(f"Created new seller: {seller}")

## get
    def get_sellers_to_process(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM sellers WHERE is_good = TRUE"
        result = self.db_client.execute_query(query)
        logging.info(f"Found {len(result)} sellers to process")
        return result
    
    def get_seller_from_sellerId(self, sellerId: str) -> Dict[str, Any]:
        query = "SELECT * FROM sellers WHERE seller = %s"
        result = self.db_client.execute_query(query, (sellerId,))[0]
        logging.info(f"Found seller: {result}")
        return result

class RepositoryForJunction:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

# create
    def create_new_junction(self, seller_id: int, product_id: int) -> None:
        query = "INSERT INTO junction (seller_id, product_id) VALUES (%s, %s)"
        self.db_client.execute_update(query, (seller_id, product_id))

class RepositoryForProductsMaster:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## create
    def create_new_product(self, asin: str) -> None:
        count = len(self.get_product_from_asin(asin))
        if count > 0:
            logging.info(f"Product {asin} already exists")
            return
        query = "INSERT INTO products_master (asin) VALUES (%s)"
        self.db_client.execute_update(query, (asin,))

## get
    def get_products_to_process(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_master WHERE last_search IS NULL OR last_search < NOW() - INTERVAL 1 MONTH AND is_good = TRUE"
        result = self.db_client.execute_query(query)
        return result

    def get_products_to_fill(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_master WHERE is_filled = FALSE"
        result = self.db_client.execute_query(query)
        logging.info(f"Found {len(result)} products to fill")
        return result
    
    def get_products_to_image_search(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_master WHERE ec_search = FALSE"
        result = self.db_client.execute_query(query)
        logging.info(f"Found {len(result)} products to image search")
        return result
    
    def get_product_from_id(self, id: int) -> Dict[str, Any]:
        query = "SELECT * FROM products_master WHERE id = %s"
        result = self.db_client.execute_query(query, (id,))[0]
        logging.info(f"Found product: {result}")
        return result
    
    def get_product_from_asin(self, asin: str) -> Dict[str, Any]:
        query = "SELECT * FROM products_master WHERE asin = %s"
        result = self.db_client.execute_query(query, (asin,))[0]
        logging.info(f"Found product: {result}")
        return result
    
## update
    def update_product_by_column(self, record: Dict[str, Any], column: str) -> None:
        columns = ['weight', 'weight_unit', 'image_url', 'last_search', 'is_good', 'is_filled', 'ec_search']
        if column not in columns:
            logging.error(f"Invalid column: {column}")
            return
        query = f"UPDATE products_masteer SET {column} = %s WHERE id = %s"
        params = (record[column], record['id'])
        self.db_client.execute_update(query, params)
        logging.info(f"Update product: {record['id']}, column: {column}")

    def update_product_status(self, record: Dict[str, Any], column: str) -> None:
        columns = ['is_filled', 'is_good', 'ec_search']
        if column not in columns:
            logging.error(f"Invalid column: {column}")
            return
        query = "UPDATE products_master SET {column} = %s WHERE id = %s"
        params = (record[column], record['id'])
        self.db_client.execute_update(query, params)
        logging.info(f"Updated product status: {column} for asin_id {record['id']}")
    
class RepositoryForProductsDetail:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## create
    def create_new_detail(self, product_id: int) -> None:
        query = "INSERT INTO products_detail (product_id) VALUES (%s)"
        self.db_client.execute_update(query, (product_id,))

## get
    def get_products_to_process(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM products_detail WHERE is_filled= FALSE"
        result = self.db_client.execute_query(query)
        logging.info(f"Found {len(result)} products to process")
        return result
    
    def get_product_from_id(self, id: int) -> Dict[str, Any]:
        query = "SELECT * FROM products_detail WHERE id = %s"
        result = self.db_client.execute_query(query, (id,))[0]
        logging.info(f"Found product: {result}")

## update
    def update_product_by_column(self, record: Dict[str, Any], column:str) -> None:
        query = f"UPDATE products_detail SET {column} = %s WHERE id = %s"
        params = (record[column], record['id'])
        self.db_client.execute_update(query, params)
        logging.info(f"Update product: {record['product_id']}, column: {column}")

class RepositoryForProductsEc:
    def __init__(self, db_client: Any) -> None:
        self.db_client = db_client

## get

## update
    def update_products_ec(self, record: Dict[str, Any]) -> None:
        product_id = record['product_id']
        ec_url = record['ec_url']
        query = "INSERT INTO products_ec (product_id, ec_url) VALUES (%s, %s)"
        self.db_client.execute_update(query, (product_id, ec_url))
        logging.info(f"Inserted new EC URL: {ec_url} for product_id {product_id}")

        

#######
def repository_for_sellers(db_client: Any) -> RepositoryForSellers:
    return RepositoryForSellers(db_client)

def repository_for_junction(db_client: Any) -> RepositoryForJunction:
    return RepositoryForJunction(db_client)

def repository_for_products_master(db_client: Any) -> RepositoryForProductsMaster:
    return RepositoryForProductsMaster(db_client)

def repository_for_products_detail(db_client: Any) -> RepositoryForProductsDetail:
    return RepositoryForProductsDetail(db_client)

def repository_for_products_ec(db_client: Any) -> RepositoryForProductsEc:
    return RepositoryForProductsEc(db_client)