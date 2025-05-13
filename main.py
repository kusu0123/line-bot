from linebot import LineBotApi, WwbhookHandler
from linebot.exceptions import InvalidSignatureError
from line.models import MessageEvent, TextMessage
from fastapi import FastAPI

from dotenv import load_dotenv

load_dotenv()

LINE_BOT_API=LineBotApi(os.environ["CHANNEL_ID"])
handler=WebhookHandler(os.environ["CHANNEL_SECRET"])
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}