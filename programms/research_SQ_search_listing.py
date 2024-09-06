import mysql.connector
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="mysql",
            database="test"
        )
        self.cursor = self.db.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        self.cursor.execute(query, params)
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()

class SearchListCreator:
    def __init__(self, db):
        self.db = db

    def create_search_list(self):
        # 現在の日時から一定期間前の日時を計算
        period = datetime.now() - timedelta(days=30)  # 例として30日前

        # products_masterテーブルから条件に合うASINを取得
        query = """
        SELECT asin FROM products_master
        WHERE last_search < %s
        """
        asins = self.db.execute_query(query, (period,))

        # researchテーブルに結果を追加
        for asin in asins:
            insert_query = """
            INSERT INTO research (asin_id, research_date)
            VALUES ((SELECT id FROM products_master WHERE asin = %s), %s)
            """
            self.db.execute_update(insert_query, (asin['asin'], datetime.now()))

            # products_masterテーブルのlast_searchを更新
            # get_detailでlast_searchを更新してもよいかもしれない
            update_query = """
            UPDATE products_master
            SET last_search = %s
            WHERE asin = %s
            """
            self.db.execute_update(update_query, (datetime.now(),asin['asin']))

if __name__ == "__main__":
    # データベース接続を作成
    db = Database()
    # サーチリスト作成オブジェクトを作成し、関数を実行
    search_list_creator = SearchListCreator(db)
    search_list_creator.create_search_list()
    # 接続を閉じる
    db.close()


