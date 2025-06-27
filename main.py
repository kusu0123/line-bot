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
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "ok"

@handler.add(MessageEvent)
def handle_message(event):
    message_text = event.message.text.lower()
    
    if "を調べる" in message_text:
        item_name_to_search = message_text.replace("を調べる", "").strip()
        LINE_BOT_API.reply_message(event.reply_token, message)
        if item_name_to_search:
            all_records=supabase.select_package_record(SUPABASE_URL)
            
            response_messages = []

            found_items_info = [] 

            for row in all_records:
                if item_name_to_search in row[0].lower(): # 大文字小文字を区別しない検索
                    last_but_one_date_str = row[1].strftime('%Y-%m-%d') if row[1] else "N/A"
                    found_items_info.append(
                        f"'{row[0]}' の情報:\n"
                        f"  前々回忘れた日付: {last_but_one_date_str}\n"
                        f"  忘れた回数: {row[2]}回"
                    )
        LINE_BOT_API.reply_message(event.reply_token, message)
    elif "を忘れた" in message_text:
        
        package_name_to_add = message_text.replace("を忘れた", "").strip()
        if package_name_to_add:
            supabase.insert_package(SUPABASE_URL, package_name_to_add)
            message = TextMessage(text=f"'{package_name_to_add}' を忘れ物リストに追加しました！")
        LINE_BOT_API.reply_message(event.reply_token, message)
    else:
        message = TextMessage(text="いつも使ってくれてありがとう")
        LINE_BOT_API.reply_message(event.reply_token, message)





