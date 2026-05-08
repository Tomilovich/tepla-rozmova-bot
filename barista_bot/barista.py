from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import get_connection

router = Router()


# ====================== СТАРТ ======================
@router.message(F.text == "/start")
async def barista_start(message: types.Message):
    await message.answer(
        "👨‍🍳 <b>Панель баристи «Тепла Розмова»</b>\n\n"
        "Оберіть дію:",
        reply_markup=barista_main_keyboard()
    )


# ====================== ГЛАВНЕ МЕНЮ ======================
def barista_main_keyboard():
    from aiogram.utils.keyboard import ReplyKeyboardBuilder
    from aiogram.types import KeyboardButton
    
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📋 Активні замовлення"))
    kb.row(KeyboardButton(text="🔄 Оновити"))
    kb.row(KeyboardButton(text="✅ Готові замовлення"))
    return kb.as_markup(resize_keyboard=True)


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
        return await message.answer("✅ На даний момент активних замовлень немає.")

    for order in orders:
        text = f"""🆔 <b>Замовлення №{order['id']}</b>
📦 {order['items']}
💰 {order['total_price']} грн
🔄 Статус: <b>{order['status']}</b>
🕒 {order['created_at'][:16]}"""

        kb = order_control_keyboard(order['id'], order['user_id'])
        await message.answer(text, reply_markup=kb)


# ====================== КЛАВІАТУРА УПРАВЛІННЯ ======================
def order_control_keyboard(order_id: int, user_id: int):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="☕ Почати готувати", callback_data=f"st_cook_{order_id}_{user_id}")
    kb.button(text="✅ Готово", callback_data=f"st_ready_{order_id}_{user_id}")
    kb.button(text="❌ Скасувати", callback_data=f"st_cancel_{order_id}_{user_id}")
    kb.adjust(1)
    return kb.as_markup()


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
    new_status = status_map.get(action, "Нове")

    with get_connection() as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))

    if new_status == "Готово":
        msg = "🌟 <b>Ваше замовлення готове!</b>\nЧекаємо вас у кав’ярні ☕"
    elif new_status == "Готується":
        msg = "⏳ Ваше замовлення <b>почали готувати</b>!"
    else:
        msg = "❌ Замовлення було скасовано."

    try:
        await callback.bot.send_message(client_id, msg)
    except:
        pass

    await callback.answer(f"Статус: {new_status}")
    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ <b>Оновлено: {new_status}</b>"
    )


   