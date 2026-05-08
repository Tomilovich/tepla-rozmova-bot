from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_connection
from keyboards import barista_main_keyboard, order_control_keyboard

router = Router()

# ====================== СТАРТ ======================
@router.message(F.text == "/start")
async def barista_start(message: types.Message):
    await message.answer(
        "👨‍🍳 <b>Панель баристи</b>\n\n"
        "Натисни кнопку для роботи:",
        reply_markup=barista_main_keyboard()
    )


# ====================== АКТИВНІ ЗАМОВЛЕННЯ ======================
@router.message(F.text.in_(["📋 Активні замовлення", "🔄 Оновити"]))
async def show_active_orders(message: types.Message):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, items, total_price, status, created_at 
            FROM orders 
            WHERE status IN ('Нове', 'Готується') 
            ORDER BY created_at DESC
        """)
        orders = cursor.fetchall()

    if not orders:
        return await message.answer("✅ Наразі немає активних замовлень.")

    text = "📋 <b>Активні замовлення:</b>\n\n"
    for order in orders:
        text += f"🆔 <b>№{order['id']}</b> — {order['status']}\n"
        text += f"📦 {order['items']}\n"
        text += f"💰 {order['total_price']} грн\n"
        text += f"🕒 {order['created_at'][:16]}\n\n"

        kb = order_control_keyboard(order['id'], order['user_id'])
        await message.answer(text, reply_markup=kb)
        text = ""  # очищаємо для наступного


# ====================== ЗМІНА СТАТУСУ ======================
@router.callback_query(F.data.startswith("st_"))
async def change_order_status(callback: types.CallbackQuery):
    data = callback.data.split("_")
    action = data[1]
    order_id = int(data[2])
    client_id = int(data[3])

    status_map = {
        "cook": "Готується",
        "ready": "Готово",
        "cancel": "Скасовано"
    }
    new_status = status_map[action]

    # Оновлюємо в базі
    with get_connection() as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))

    # Повідомляємо клієнта
    if new_status == "Готово":
        msg = "🌟 <b>Ваше замовлення готове!</b>\nЧекаємо на вас у кав’ярні ☕"
    elif new_status == "Готується":
        msg = "⏳ Ваше замовлення <b>почали готувати</b>!"
    else:
        msg = "❌ Замовлення скасовано."

    try:
        await callback.bot.send_message(client_id, msg)
    except:
        pass

    await callback.answer(f"Статус змінено на: {new_status}")
    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ <b>Статус: {new_status}</b>"
    )