from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

def barista_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📋 Активні замовлення"))
    kb.row(KeyboardButton(text="🔄 Оновити"))
    kb.row(KeyboardButton(text="✅ Готові замовлення"))
    return kb.as_markup(resize_keyboard=True)


def order_control_keyboard(order_id: int, user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="☕ Почати готувати", callback_data=f"st_cook_{order_id}_{user_id}")
    kb.button(text="✅ Готово", callback_data=f"st_ready_{order_id}_{user_id}")
    kb.button(text="❌ Скасувати", callback_data=f"st_cancel_{order_id}_{user_id}")
    kb.adjust(1)
    return kb.as_markup()


# ====================== КЛАВІАТУРА ДЛЯ БАРИСТИ ======================
def order_control_keyboard(order_id: int, user_id: int):
    """Клавіатура, яку бачить бариста під новим замовленням"""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="☕ Почати готувати", callback_data=f"st_cook_{order_id}_{user_id}")
    kb.button(text="✅ Готово", callback_data=f"st_ready_{order_id}_{user_id}")
    kb.button(text="❌ Скасувати", callback_data=f"st_cancel_{order_id}_{user_id}")
    kb.adjust(1)
    return kb.as_markup()