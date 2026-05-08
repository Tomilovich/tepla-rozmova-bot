from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from menu import MENU

router = Router()


# ====================== ДОПОМІЖНІ ФУНКЦІЇ ======================

def calculate_total(cart: dict) -> int:
    total = 0

    # Десерти
    for dessert in cart.get("desserts", []):
        total += dessert.get("price", 0) * dessert.get("quantity", 1)

    # Напої
    for key, items in cart.items():
        if key == "desserts":
            continue

        drink = MENU.get(key)
        if not drink:
            continue

        for item in items:
            total += drink.get("price", 0) * item.get("quantity", 1)

    return total


# ====================== ВІДОБРАЖЕННЯ КОШИКА ======================

async def show_cart(event: types.Message | types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", {})

    if not cart:
        text = "🛒 <b>Ваш кошик порожній</b>\n\nЧас замовити щось смачне ☕"
        kb = None
    else:
        text = "🛒 <b>Ваш кошик — Тепла Розмова</b>\n\n"
        builder = InlineKeyboardBuilder()

        # ===== ДЕСЕРТИ =====
        for i, dessert in enumerate(cart.get("desserts", [])):
            qty = dessert.get("quantity", 1)
            price_line = dessert.get("price", 0) * qty

            text += f"🍰 {dessert.get('name')} ×{qty} — {price_line} грн\n"

            builder.button(text="➖", callback_data=f"dec_desserts_{i}")
            builder.button(text="➕", callback_data=f"inc_desserts_{i}")
            builder.button(text="🗑", callback_data=f"remove_dessert_{i}")

        # ===== НАПОЇ =====
        for key, items in cart.items():
            if key == "desserts":
                continue

            drink = MENU.get(key)
            if not drink:
                continue

            for i, item in enumerate(items):
                qty = item.get("quantity", 1)
                price_line = drink.get("price", 0) * qty

                text += f"☕ {drink.get('name')} ({item.get('size', 'M')}) ×{qty} — {price_line} грн\n"

                builder.button(text="➖", callback_data=f"dec_{key}_{i}")
                builder.button(text="➕", callback_data=f"inc_{key}_{i}")
                builder.button(text="🗑", callback_data=f"remove_{key}_{i}")

        total = calculate_total(cart)
        text += f"\n━━━━━━━━━━━━━━\n<b>Разом: {total} грн</b>"

        # ===== КНОПКИ =====
        builder.button(text="✅ Оформити замовлення", callback_data="checkout")
        builder.button(text="☕ Замовити ще", callback_data="order_more")
        builder.button(text="🗑 Очистити кошик", callback_data="clear_cart")

        builder.adjust(3)  # акуратна сітка
        kb = builder.as_markup()

    # ===== ВІДПРАВКА =====
    try:
        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(text, reply_markup=kb)
        else:
            await event.answer(text, reply_markup=kb)
    except Exception as e:
        print(f"[ERROR show_cart]: {e}")
        if isinstance(event, types.CallbackQuery):
            await event.message.answer(text, reply_markup=kb)


# ====================== ОБРОБНИКИ ======================

@router.callback_query(lambda c: c.data.startswith("inc_"))
async def inc_quantity(callback: types.CallbackQuery, state: FSMContext):
    _, key, idx = callback.data.split("_")
    idx = int(idx)

    data = await state.get_data()
    cart = data.get("cart", {})

    if key == "desserts":
        if idx < len(cart.get("desserts", [])):
            cart["desserts"][idx]["quantity"] = cart["desserts"][idx].get("quantity", 1) + 1
    elif key in cart and idx < len(cart[key]):
        cart[key][idx]["quantity"] = cart[key][idx].get("quantity", 1) + 1

    await state.update_data(cart=cart)
    await callback.answer("➕ Додано")
    await show_cart(callback, state)


@router.callback_query(lambda c: c.data.startswith("dec_"))
async def dec_quantity(callback: types.CallbackQuery, state: FSMContext):
    _, key, idx = callback.data.split("_")
    idx = int(idx)

    data = await state.get_data()
    cart = data.get("cart", {})

    def decrease(items, index):
        if index >= len(items):
            return
        qty = items[index].get("quantity", 1)
        if qty > 1:
            items[index]["quantity"] = qty - 1
        else:
            items.pop(index)

    if key == "desserts":
        decrease(cart.get("desserts", []), idx)
        if not cart.get("desserts"):
            cart.pop("desserts", None)
    elif key in cart:
        decrease(cart[key], idx)
        if not cart[key]:
            cart.pop(key)

    await state.update_data(cart=cart)
    await callback.answer("➖ Зменшено")
    await show_cart(callback, state)


@router.callback_query(lambda c: c.data.startswith("remove_"))
async def remove_item(callback: types.CallbackQuery, state: FSMContext):
    _, key, idx = callback.data.split("_")
    idx = int(idx)

    data = await state.get_data()
    cart = data.get("cart", {})

    if key == "dessert":
        if idx < len(cart.get("desserts", [])):
            cart["desserts"].pop(idx)
            if not cart["desserts"]:
                cart.pop("desserts")
    elif key in cart and idx < len(cart[key]):
        cart[key].pop(idx)
        if not cart[key]:
            cart.pop(key)

    await state.update_data(cart=cart)
    await callback.answer("🗑 Видалено")
    await show_cart(callback, state)


@router.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(cart={})
    await callback.answer("🧹 Кошик очищено")
    await callback.message.edit_text("🛒 Кошик очищено.")


@router.callback_query(lambda c: c.data == "order_more")
async def order_more(callback: types.CallbackQuery, state: FSMContext):
    from .order import start_order
    await start_order(callback.message, state)


@router.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery, state: FSMContext):
    from .review import start_checkout
    await start_checkout(callback, state)