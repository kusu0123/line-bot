import os
import psycopg
# データを入れ込む関数
def insert_package(conn_str:str,package_name:str):
    print(f"\n--- INSERTクエリの実行 ('{package_name}' を追加) ---")
    try:
        with psycopg.connect(conn_str) as conn:
                with conn.cursor() as cur:
                    sql_query = """
                WITH inserted_package AS (
                    INSERT INTO package(name) VALUES (%s) RETURNING id
                )
                INSERT INTO record(package_id, date)
                SELECT id, CURRENT_DATE FROM inserted_package;
                """
                cur.execute(sql_query, (package_name,))
                print(f"'{package_name}' のパッケージと関連レコードが追加されました。")
    except psycopg.Error as e:
        print(f"データベースエラーが発生しました: {e}")

# データを取ってくる関数 
def select_package_record(conn_str:str):
    print("--- SELECTクエリの実行 ---")
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                sql_query = "SELECT package.name,MAX(CASE WHEN record_ranked rn=2 THEN record_ranked.date END) AS m, COUNT(record.package_id) FROM package JOIN record ON package.id=record.package_id GROUP BY m DNSC;"
                
                cur.execute(sql_query)
                
                results = cur.fetchall()
                
                if results:
                    print("取得結果:")
                    for row in results:
                        print(f"  忘れ物名: {row[0]}, 前々回忘れた日付: {row[1]}, 忘れた回数: {row[2]}")
                else:
                    print("データが見つかりませんでした。")
                    
    except psycopg.Error as e:
        print(f"データベースエラーが発生しました: {e}")
