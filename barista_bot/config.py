import os
from dotenv import load_dotenv

load_dotenv()

BARISTA_BOT_TOKEN = os.getenv("BARISTA_BOT_TOKEN")
BARISTA_CHAT_ID = int(os.getenv("BARISTA_CHAT_ID"))

if not BARISTA_BOT_TOKEN:
    raise ValueError("❌ BARISTA_BOT_TOKEN не знайдено в .env!")