import requests

# ==============================================================================
# この関数をコピーして、あなたのLINE Botのプログラムに貼り付けてください
# ==============================================================================
def check_supabase_access_with_url_key():
    """
    SupabaseのURLとAPIキーを使って、REST API経由でアクセスできるか確認する関数
    """
    
    # ▼▼▼ ここにあなたの情報を入力してください！ ▼▼▼
    
    # Supabase管理画面 > Project Settings > API で確認できるURL
    SUPABASE_URL = "https://<YOUR_PROJECT_ID>.supabase.co"
    
    # Supabase管理画面 > Project Settings > API で確認できる `anon` `public` キー
    SUPABASE_KEY = "<YOUR_SUPABASE_ANON_KEY>"
    
    # アクセスを確認したい、あなたが作成したテーブルの名前
    TABLE_NAME = "your_table_name" 

    # ▲▲▲ 入力はここまで ▲▲▲
    
    
    # --- 以下はプログラムの処理なので、変更は不要です ---
    
    # APIにリクエストを送るためのURLを組み立て
    api_endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*&limit=1"

    # リクエストヘッダーにAPIキーを設定
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    print(f"Supabase API ({TABLE_NAME}テーブル) へのアクセスを開始します...")

    try:
        # SupabaseにHTTP GETリクエストを送信
        response = requests.get(api_endpoint, headers=headers, timeout=10)

        # HTTPステータスコードで成功か失敗かを判断
        if 200 <= response.status_code < 300:
            print("✅ 接続成功！ Supabaseから正常な応答がありました。")
            # print("受信データ:", response.json()) # データの中身を見たい場合はこの行のコメントを外す
            return True
        else:
            print(f"❌ アクセス失敗 (HTTPステータスコード: {response.status_code})")
            print(f"   エラー内容: {response.json()}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ ネットワークエラーが発生しました。インターネット接続やURLを確認してください。")
        print(f"   エラー詳細: {e}")
        return False

# ==============================================================================
# この関数を呼び出して、実際に接続を確認する
# (この部分は、あなたのBotの好きなタイミングで呼び出すように変更してください)
# ==============================================================================
if __name__ == "__main__":
    is_ok = check_supabase_access_with_url_key()

    if is_ok:
        print("\nLINE BotはSupabaseの機能を利用できます。")
    else:
        print("\nSupabaseに接続できませんでした。設定を確認してください。")