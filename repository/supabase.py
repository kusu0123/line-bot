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
                    INSERT INTO package(name) 
                    VALUES (%s) 
                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id
                )
                INSERT INTO record(package_id, date)
                SELECT id, CURRENT_DATE FROM inserted_package;
                """
                cur.execute(sql_query, (package_name,))
                print(f"'{package_name}' のパッケージと関連レコードが追加されました。")
    except psycopg.Error as e:
        print(f"データベースエラーが発生しました: {e}")
    except Exception as e:  # その他の予期せぬエラーもキャッチする
        print(f"予期せぬエラーが発生しました: {e}")
# データを取ってくる関数 
def select_package_record(conn_str:str):
    print("--- SELECTクエリの実行 ---")
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                sql_query ="""
                 SELECT 
                        package.name, 
                        MAX(record.date) AS last_date, 
                        COUNT(record.package_id) AS forget_count
                    FROM 
                        package 
                    JOIN 
                        record 
                    ON 
                        package.id = record.package_id
                    GROUP BY 
                        package.name
                    ORDER BY 
                        last_date DESC;
                """
                cur.execute(sql_query)
                results = cur.fetchall()
                
                if results:
                    print("取得結果:")
                    for row in results:
                        print(f"  忘れ物名: {row[0]}, 前々回忘れた日付: {row[1]}, 忘れた回数: {row[2]}")
                else:
                    print("データが見つかりませんでした。")
                return results    
    except psycopg.Error as e:
        print(f"データベースエラーが発生しました: {e}")
        return None
    except Exception as e: 
        print(f"予期せぬエラーが発生しました: {e}")
        return None
