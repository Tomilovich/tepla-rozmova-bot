from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton


# ====================== ГОЛОВНЕ МЕНЮ ======================

def main_menu_keyboard():
    kb = ReplyKeyboardBuilder()

    kb.row(
        KeyboardButton(text="☕ Замовити каву"),
        KeyboardButton(text="🍰 Солодощі")
    )
    kb.row(
        KeyboardButton(text="🛒 Кошик"),
        KeyboardButton(text="🔄 Повторити останнє")
    )
    kb.row(
        KeyboardButton(text="❤️ Улюблені"),
        KeyboardButton(text="🎁 Бонуси")
    )
    kb.row(
        KeyboardButton(text="🌟 Рекомендація"),
        KeyboardButton(text="Вгадай смак")
    )
    

    return kb.as_markup(resize_keyboard=True)


# ====================== INLINE КЛАВІАТУРА ======================

def inline_kb(items: list, prefix: str, width: int = 2):
    """
    Універсальна inline-клавіатура
    prefix — тип дії (cat, size, milk...)
    """

    builder = InlineKeyboardBuilder()

    if not items:
        return None

    for item in items:
        builder.button(
            text=str(item),
            callback_data=f"{prefix}_{item}"  # 🔥 ГОЛОВНИЙ ФІКС
        )

    builder.adjust(width)
    return builder.as_markup()


# ====================== ТАК / НІ ======================

def yes_no_kb(prefix: str):
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Так", callback_data=f"{prefix}_yes")
    builder.button(text="❌ Ні", callback_data=f"{prefix}_no")

    builder.adjust(2)

    return builder.as_markup()


def order_control_keyboard(order_id: int, user_id: int):
    """Клавіатура для баристи"""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="☕ Почати готувати", callback_data=f"st_cook_{order_id}_{user_id}")
    kb.button(text="✅ Готово", callback_data=f"st_ready_{order_id}_{user_id}")
    kb.button(text="❌ Скасувати", callback_data=f"st_cancel_{order_id}_{user_id}")
    kb.adjust(1)
    return kb.as_markup()