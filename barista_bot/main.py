import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

from config import BARISTA_BOT_TOKEN
from database import get_connection, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# ====================== КЛАВІАТУРИ ======================
def main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📋 Активні замовлення"))
    kb.row(KeyboardButton(text="🔄 Оновити"))
    return kb.as_markup(resize_keyboard=True)

def order_kb(order_id: int, user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="☕ Почати готувати", callback_data=f"st_cook_{order_id}_{user_id}")
    kb.button(text="✅ Готово", callback_data=f"st_ready_{order_id}_{user_id}")
    kb.button(text="❌ Скасувати", callback_data=f"st_cancel_{order_id}_{user_id}")
    kb.adjust(1)
    return kb.as_markup()

# ====================== ОСНОВНИЙ КОД ======================
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("👨‍🍳 <b>Панель баристи</b>\n\nНатискай кнопки нижче:", reply_markup=main_keyboard())

@dp.message(F.text.in_(["📋 Активні замовлення", "🔄 Оновити"]))
async def show_orders(message: types.Message):
    with get_connection() as conn:
        orders = conn.execute("""
            SELECT id, user_id, items, total_price, status, created_at 
            FROM orders 
            WHERE status IN ('Нове', 'Готується') 
            ORDER BY created_at DESC
        """).fetchall()

    if not orders:
        return await message.answer("✅ Активних замовлень немає.")

    for order in orders:
        text = f"""🆔 <b>Замовлення №{order['id']}</b>
📦 {order['items']}
💰 {order['total_price']} грн
🔄 Статус: <b>{order['status']}</b>
🕒 {order['created_at'][:16]}"""

        await message.answer(text, reply_markup=order_kb(order['id'], order['user_id']))

@dp.callback_query(F.data.startswith("st_"))
async def change_status(callback: types.CallbackQuery):
    action, order_id, user_id = callback.data.split("_")[1:]
    order_id = int(order_id)
    user_id = int(user_id)

    status_map = {"cook": "Готується", "ready": "Готово", "cancel": "Скасовано"}
    new_status = status_map.get(action, "Нове")

    with get_connection() as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))

    # Повідомлення клієнту
    texts = {
        "Готується": "⏳ Ваше замовлення почали готувати!",
        "Готово": "🌟 Ваше замовлення готове! Чекаємо на вас ☕",
        "Скасовано": "❌ Замовлення скасовано."
    }
    try:
        await callback.bot.send_message(user_id, texts.get(new_status, "Статус оновлено"))
    except:
        pass

    await callback.answer(f"✓ {new_status}")
    await callback.message.edit_text(callback.message.text + f"\n\n✅ <b>Статус: {new_status}</b>")

# ====================== ЗАПУСК ======================
async def main():
    if not BARISTA_BOT_TOKEN:
        logging.error("❌ BARISTA_BOT_TOKEN не знайдено!")
        return

    bot = Bot(token=BARISTA_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    init_db()
    logging.info("👨‍🍳 Бариста-бот успішно запущено!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())