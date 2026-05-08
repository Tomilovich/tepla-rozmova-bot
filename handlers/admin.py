from aiogram import Router, types, F
from database import get_connection

router = Router()

@router.callback_query(F.data.startswith("st_"))
async def change_status(callback: types.CallbackQuery):
    # Розпаковуємо дані: статус, ID замовлення, ID клієнта
    data = callback.data.split("_")
    status_type = data[1]
    order_id = data[2]
    client_id = int(data[3])

    if status_type == "cook":
        new_status = "Готується"
        user_msg = "⏳ Ваше замовлення вже <b>готується</b>!"
    else:
        new_status = "Готово"
        user_msg = "🌟 <b>Ваше замовлення готове!</b>\nЧекаємо на вас: вул. Хрещатик, 22 ☕"

    # Оновлюємо статус у базі
    with get_connection() as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))

    await callback.answer(f"Статус: {new_status}")
    await callback.message.edit_text(callback.message.text + f"\n\nСтатус: <b>{new_status}</b>")

    # Надсилаємо клієнту повідомлення про статус
    try:
        await callback.bot.send_message(client_id, user_msg)
    except Exception:
        pass