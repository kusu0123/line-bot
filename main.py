from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage,ImageSendMessage
from fastapi import FastAPI, Request, BackgroundTasks, Header
from dotenv import load_dotenv
from starlette.exceptions import HTTPException
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

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
    
    if "こんにちは" in message_text:
        message = TextMessage(text="こんにちは！！")
        LINE_BOT_API.reply_message(event.reply_token, message)
    elif "ありがとう" in message_text:
        message = TextMessage(text="こちらこそー")
        LINE_BOT_API.reply_message(event.reply_token, message)
    elif"犬"in message_text:
        message = ImageSendMessage(
        original_content_url="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj0Uk0AZltkvruXawqvtOXHnVPBoLB6hEo-SDh4ouG9bGZnH4IaxxSGJZjehyphenhyphenvHHzRNDSNHPfTdatbR8bDmWXPhc4zzJtx7fIuLeJFPVJhfQkFp4LSqSR94mUZHJoqHtpMpe2Nu9p1pztSP/s1600/dog_sleep_run.png", # フルサイズ画像URL（HTTPS必須）
        preview_image_url="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj0Uk0AZltkvruXawqvtOXHnVPBoLB6hEo-SDh4ouG9bGZnH4IaxxSGJZjehyphenhyphenvHHzRNDSNHPfTdatbR8bDmWXPhc4zzJtx7fIuLeJFPVJhfQkFp4LSqSR94mUZHJoqHtpMpe2Nu9p1pztSP/s1600/dog_sleep_run.png"     # プレビュー画像URL（同じでもOK）
        )
        LINE_BOT_API.reply_message(event.reply_token, message)
    else:
        message = TextMessage(text="いつも使ってくれてありがとう")
        LINE_BOT_API.reply_message(event.reply_token, message)





