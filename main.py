import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN, CAFE_NAME
from database import init_db

# Імпорт всіх роутерів (БЕЗ admin_router!)
from handlers import (
    start_router,
    profile_router,
    quiz_router,
    order_router,
    cart_router,
    review_router
    # admin_router — видалено!
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

async def main():
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Підключаємо роутери
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(quiz_router)
    dp.include_router(order_router)
    dp.include_router(cart_router)
    dp.include_router(review_router)

    init_db()

    logging.info(f"☕ Бот «{CAFE_NAME}» успішно запущено!")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())