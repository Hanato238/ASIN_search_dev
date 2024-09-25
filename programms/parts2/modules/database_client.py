import mysql.connector
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DatabaseClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        if not hasattr(self, 'initialized'):
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            logging.info("Connected to database")
            self.initialized = True

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        logging.info(f"executing query: {query} with params: {params}")
        self.cursor.execute(query, params or ())
        result = self.cursor.fetchall()
        logging.info(f"Query executed successfully")
        return result

    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        logging.info("executing update query")
        self.cursor.execute(query, params or ())
        self.connection.commit()
        logging.info("Update committed")

    def close(self) -> None:
        logging.info("Closing database connection")
        self.cursor.close()
        self.connection.close()
        logging.info("Database connection closed")

def database_client(host: str, user: str, password: str, database: str):
    return DatabaseClient(host, user, password, database)