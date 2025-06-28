from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage,ImageSendMessage
from fastapi import FastAPI, Request, BackgroundTasks, Header
from dotenv import load_dotenv
from starlette.exceptions import HTTPException
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

from repository import supabase

load_dotenv()

LINE_BOT_API=LineBotApi(os.environ["ACCESS_TOKEN"])
handler=WebhookHandler(os.environ["CHANNEL_SECRET"])


USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

SUPABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

engine = create_engine(SUPABASE_URL)

app = FastAPI()

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")               
        
        

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature=Header(None),
):
    body = await request.body()

    try:
        # 非同期タスクから同期処理に変更
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "ok"

@handler.add(MessageEvent)
def handle_message(event):
    message_text = event.message.text.lower()
    reply_message = TextMessage(text="メッセージをありがとう！\n「〜を調べる」または「〜を忘れた」と話しかけてみてね。") 
    if "を調べる" in message_text:
        item_name_to_search = message_text.replace("を調べる", "").strip()
        
        if not item_name_to_search:
            # 検索キーワードが空の場合
            reply_message = TextMessage(text="調べたい忘れ物の名前を入力してください。\n例: '傘を調べる'")
        else:
            # 検索キーワードがある場合 (データベースエラーが発生した場合、ここでクラッシュします)
            all_records = supabase.select_package_record(SUPABASE_URL)
            
            found_items_info = [] 
            if all_records: # レコードが取得できた場合のみ処理
                for row in all_records:
                    # 検索語句が忘れ物名の一部に含まれるかチェック (大文字小文字を区別しない)
                    if item_name_to_search in row[0].lower():
                        # row[1] は日付オブジェクト（前回忘れた日付）
                        last_forgot_date_str = row[1].strftime('%Y-%m-%d') if row[1] else "N/A"
                        found_items_info.append(
                            f"'{row[0]}' の情報:\n"
                            f"  前回忘れた日付: {last_forgot_date_str}\n" # 文言修正
                            f"  忘れた回数: {row[2]}回"
                        )
            
            if found_items_info:
                # 見つかったアイテム情報を結合して一つのメッセージとして返信
                reply_message = TextMessage(text="\n\n".join(found_items_info))
            else:
                # 検索結果がなかった場合
                reply_message = TextMessage(text=f"'{item_name_to_search}' の忘れ物は見つかりませんでした。")
    elif "を忘れた" in message_text:
        package_name_to_add = message_text.replace("を忘れた", "").strip()
        
        if not package_name_to_add:
            reply_message = TextMessage(text="忘れ物として追加したい名前を入力してください。\n例: '鍵を忘れた'")
        else:
            supabase.insert_package(SUPABASE_URL, package_name_to_add)
            reply_message = TextMessage(text=f"'{package_name_to_add}' を忘れ物リストに追加しました！")
    
    LINE_BOT_API.reply_message(event.reply_token,reply_message)





