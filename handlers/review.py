from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import OrderStates
from database import get_user_data, spend_bonuses, save_order, save_last_order
from .cart import calculate_total
from keyboards import inline_kb, main_menu_keyboard, order_control_keyboard   # ← важливо!

from menu import MENU

router = Router()


# ====================== СТАРТ ОФОРМЛЕННЯ ======================
@router.callback_query(lambda c: c.data == "checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "🚚 <b>Оберіть спосіб отримання:</b>",
        reply_markup=inline_kb(["Самовивіз", "Доставка"], "pickup")
    )
    await state.set_state(OrderStates.choosing_pickup)


# ====================== ВИБІР ДОСТАВКИ ======================
@router.callback_query(lambda c: c.data.startswith("pickup_"))
async def choose_pickup(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    pickup_type = callback.data.split("_")[1]
    await state.update_data(pickup_type=pickup_type)

    if pickup_type == "Доставка":
        await state.set_state(OrderStates.entering_address)
        await callback.message.edit_text(
            "📍 <b>Вкажіть адресу доставки:</b>\n\nПриклад: вул. Хрещатик 22, Київ"
        )
    else:
        cafe_address = "м. Київ, вул. Хрещатик, 22"
        await state.update_data(address=cafe_address)
        await callback.message.answer(
            f"✅ <b>Обрано самовивіз</b>\nЧекаємо на вас за адресою: <b>{cafe_address}</b>"
        )
        await show_order_confirmation(callback, state)


# ====================== ВВЕДЕННЯ АДРЕСИ ======================
@router.message(OrderStates.entering_address)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 10:
        return await message.answer("❌ Введіть більш повну адресу")
    await state.update_data(address=address)
    await show_order_confirmation(message, state)


# ====================== ПІДТВЕРДЖЕННЯ ЗАМОВЛЕННЯ ======================
async def show_order_confirmation(event: types.Message | types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", {})

    if not cart:
        text = "❌ Кошик порожній"
        return await (event.answer(text) if isinstance(event, types.Message) else event.message.edit_text(text))

    total = calculate_total(cart)
    user = get_user_data(event.from_user.id if isinstance(event, types.Message) else event.from_user.id) or {}
    bonuses = user.get("bonuses", 0)

    text = "<b>📋 Підтвердження замовлення</b>\n\n"

    # Товари
    for d in cart.get("desserts", []):
        qty = d.get("quantity", 1)
        text += f"🍰 {d.get('name')} ×{qty} — {d.get('price',0)*qty} грн\n"

    for drink_id, items in cart.items():
        if drink_id == "desserts": continue
        drink = MENU.get(drink_id)
        if drink:
            for item in items:
                qty = item.get("quantity", 1)
                text += f"☕ {drink.get('name')} ×{qty} — {drink.get('price',0)*qty} грн\n"

    text += f"\n━━━━━━━━━━━━━━\n"
    text += f"<b>Спосіб:</b> {data.get('pickup_type')}\n"
    if data.get("address"):
        text += f"<b>Адреса:</b> {data['address']}\n"
    text += f"🎁 Бонуси: <b>{bonuses}</b> грн\n"
    text += f"<b>Разом: {total} грн</b>"

    # Кнопки
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Підтвердити", callback_data="confirm_no_bonus")
    if bonuses >= 100:
        kb.button(text="🎟️ Використати бонуси", callback_data="confirm_with_bonus")
    kb.button(text="❌ Скасувати", callback_data="cancel_order")
    kb.adjust(1)

    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=kb.as_markup())
    else:
        await event.message.edit_text(text, reply_markup=kb.as_markup())


# ====================== ФІНАЛЬНЕ ПІДТВЕРДЖЕННЯ ======================
@router.callback_query(lambda c: c.data.startswith("confirm_"))
async def final_confirm(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    cart = data.get("cart", {})
    user_id = callback.from_user.id

    if not cart:
        return await callback.message.edit_text("❌ Кошик порожній")

    use_bonus = callback.data == "confirm_with_bonus"
    if use_bonus:
        spend_bonuses(user_id)

    # Формуємо текст замовлення
    summary_list = []
    for d in cart.get("desserts", []):
        summary_list.append(f"{d['name']} (x{d['quantity']})")
    for drink_id, items in cart.items():
        if drink_id == "desserts": continue
        drink = MENU.get(drink_id)
        if drink:
            for item in items:
                summary_list.append(f"{drink['name']} (x{item['quantity']})")

    items_text = ", ".join(summary_list)
    total_price = calculate_total(cart)
    final_amount = total_price - 50 if use_bonus else total_price
    if final_amount < 0:
        final_amount = 0

    pickup_type = data.get("pickup_type", "Самовивіз")
    address = data.get("address", "вул. Хрещатик, 22")

    # Зберігаємо замовлення
    order_id = save_order(user_id, items_text, final_amount, pickup_type, address)
    save_last_order(user_id, cart)

    # Відправка баристі
    from config import BARISTA_BOT_TOKEN, BARISTA_CHAT_ID
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    barista_bot = Bot(
        token=BARISTA_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    admin_text = (
        f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ №{order_id}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 Клієнт: {callback.from_user.full_name}\n"
        f"📦 {items_text}\n"
        f"💰 {final_amount} грн\n"
        f"📍 {pickup_type}\n"
        f"🏠 {address}"
    )

    kb = order_control_keyboard(order_id, user_id)

    try:
        await barista_bot.send_message(BARISTA_CHAT_ID, admin_text, reply_markup=kb)
    except Exception as e:
        print(f"Помилка відправки баристі: {e}")

    # Відповідь клієнту
    await callback.message.edit_text(
        f"🎉 <b>Замовлення №{order_id} прийнято!</b>\n\n"
        f"Ми вже починаємо готувати вашу каву ❤️\n"
        f"Очікуйте повідомлення про готовність!"
    )

    await state.clear()
    await callback.message.answer("Головне меню 👇", reply_markup=main_menu_keyboard())


# ====================== ПІДТВЕРДЖЕННЯ ЗАМОВЛЕННЯ ======================
@router.callback_query(F.data.startswith("confirm_"))
async def final_confirm(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("✅ Обробляємо замовлення...")

    data = await state.get_data()
    cart = data.get("cart", {})

    if not cart:
        return await callback.message.edit_text("❌ Кошик порожній")

    # Використання бонусів
    use_bonus = callback.data == "confirm_with_bonus"
    if use_bonus:
        from database import spend_bonuses
        spend_bonuses(callback.from_user.id)

    # Формуємо список товарів
    summary = []
    for d in cart.get("desserts", []):
        summary.append(f"{d.get('name')} (x{d.get('quantity', 1)})")
    
    for drink_id, items in list(cart.items()):
        if drink_id == "desserts":
            continue
        drink = MENU.get(drink_id)
        if drink:
            for item in items:
                summary.append(f"{drink['name']} (x{item.get('quantity', 1)})")

    items_text = ", ".join(summary)
    total_price = calculate_total(cart)
    final_amount = total_price - 50 if use_bonus else total_price

    pickup = data.get("pickup_type", "Самовивіз")
    address = data.get("address", "м. Київ, вул. Хрещатик, 22")

    # Зберігаємо замовлення
    from database import save_order, save_last_order
    order_id = save_order(callback.from_user.id, items_text, final_amount, pickup, address)
    save_last_order(callback.from_user.id, cart)

    # Відправка баристі
    try:
        from config import BARISTA_BOT_TOKEN, BARISTA_CHAT_ID
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from keyboards import order_control_keyboard

        barista_bot = Bot(
            token=BARISTA_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        admin_text = f"""🔔 <b>НОВЕ ЗАМОВЛЕННЯ №{order_id}</b>
👤 {callback.from_user.full_name}
📦 {items_text}
💰 {final_amount} грн
📍 {pickup} — {address}"""

        kb = order_control_keyboard(order_id, callback.from_user.id)
        await barista_bot.send_message(BARISTA_CHAT_ID, admin_text, reply_markup=kb)
    except Exception as e:
        print(f"Помилка відправки баристі: {e}")

    # Повідомлення клієнту
    await callback.message.edit_text(
        f"🎉 <b>Замовлення №{order_id} успішно прийнято!</b>\n\n"
        "Ми вже починаємо готувати вашу каву ❤️\n"
        "Очікуйте повідомлення про готовність!"
    )

    await state.clear()
    await callback.message.answer("Головне меню 👇", reply_markup=main_menu_keyboard())