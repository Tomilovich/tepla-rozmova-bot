from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== ОСНОВНИЙ БОТ (Клієнтський) ====================
TOKEN: str | None = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено в .env файлі!")

ADMIN_ID: int = 525425758                    # твій ID (можна залишити)

CAFE_NAME: str = os.getenv("CAFE_NAME", "Тепла Розмова")


# ==================== БАРИСТА БОТ ====================
BARISTA_BOT_TOKEN: str | None = os.getenv("BARISTA_BOT_TOKEN")
BARISTA_CHAT_ID: int = int(os.getenv("BARISTA_CHAT_ID", 0))

if not BARISTA_BOT_TOKEN:
    print("⚠️ Попередження: BARISTA_BOT_TOKEN не знайдено в .env")
if BARISTA_CHAT_ID == 0:
    print("⚠️ Попередження: BARISTA_CHAT_ID не налаштовано")


# ==================== ФОТО ТА ІНШЕ (залишаємо як було) ====================
MAIN_PHOTO: str = os.getenv(
    "MAIN_PHOTO",
    "https://images.pexels.com/photos/33621902/pexels-photo-33621902.jpeg"
)

START_ALBUM: List[str] = [
    os.getenv("PHOTO_1", "https://images.pexels.com/photos/33621902/pexels-photo-33621902.jpeg"),
    os.getenv("PHOTO_2", "https://images.pexels.com/photos/14704904/pexels-photo-14704904.jpeg"),
    os.getenv("PHOTO_3", "https://images.pexels.com/photos/33856911/pexels-photo-33856911.jpeg"),
    os.getenv("PHOTO_4", "https://images.pexels.com/photos/12176271/pexels-photo-12176271.jpeg"),
]
START_ALBUM = [url for url in START_ALBUM if url]