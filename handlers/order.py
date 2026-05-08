from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import OrderStates
from menu import MENU, DESSERTS, SIZES, MILKS, SYRUPS, SHOTS
from keyboards import inline_kb, main_menu_keyboard
from database import get_user_data, save_order, save_last_order, spend_bonuses
from .cart import show_cart, calculate_total
from config import BARISTA_BOT_TOKEN, BARISTA_CHAT_ID
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

router = Router()


# ====================== ЗАМОВЛЕННЯ КАВИ ======================

@router.message(lambda m: m.text == "☕ Замовити каву")
async def start_order(message: types.Message, state: FSMContext):
    await state.set_state(OrderStates.choosing_category)
    await message.answer("☕ <b>Оберіть напій:</b>", reply_markup=inline_kb(list(MENU.keys()), "cat"))


@router.callback_query(lambda c: c.data.startswith("cat_"))
async def choose_drink(callback: types.CallbackQuery, state: FSMContext):
    drink_id = callback.data.split("_")[1]
    drink = MENU.get(drink_id)
    if not drink:
        return await callback.answer("❌ Напій не знайдено")

    await state.update_data(drink_id=drink_id)
    await state.set_state(OrderStates.choosing_size)

    await callback.message.edit_text(
        f"☕ Ви обрали: <b>{drink['name']}</b>\n\nОберіть розмір:",
        reply_markup=inline_kb(SIZES, "size")
    )


@router.callback_query(lambda c: c.data.startswith("size_"))
async def choose_size(callback: types.CallbackQuery, state: FSMContext):
    size = callback.data.split("_")[1]
    await state.update_data(size=size)
    await state.set_state(OrderStates.choosing_milk)

    await callback.message.edit_text(
        "🥛 Оберіть тип молока:",
        reply_markup=inline_kb(MILKS, "milk")
    )


@router.callback_query(lambda c: c.data.startswith("milk_"))
async def choose_milk(callback: types.CallbackQuery, state: FSMContext):
    milk = callback.data.split("_")[1]
    await state.update_data(milk=milk)
    await state.set_state(OrderStates.choosing_syrup)

    await callback.message.edit_text(
        "🍯 Оберіть сироп:",
        reply_markup=inline_kb(SYRUPS, "syrup")
    )


@router.callback_query(lambda c: c.data.startswith("syrup_"))
async def choose_syrup(callback: types.CallbackQuery, state: FSMContext):
    syrup = callback.data.split("_")[1]
    await state.update_data(syrup=syrup)
    await state.set_state(OrderStates.choosing_shots)

    await callback.message.edit_text(
        "⚡ Кількість шотів еспресо:",
        reply_markup=inline_kb(SHOTS, "shots")
    )


@router.callback_query(lambda c: c.data.startswith("shots_"))
async def choose_shots(callback: types.CallbackQuery, state: FSMContext):
    try:
        shots = int(callback.data.split("_")[1])
    except:
        return await callback.answer("❌ Помилка")

    data = await state.get_data()
    drink_id = data.get("drink_id")
    drink = MENU.get(drink_id)
    if not drink:
        return await callback.answer("❌ Напій не знайдено")

    cart = data.get("cart", {})
    cart.setdefault(drink_id, [])
    cart[drink_id].append({
        "size": data.get("size"),
        "milk": data.get("milk"),
        "syrup": data.get("syrup"),
        "shots": shots,
        "quantity": 1
    })

    await state.update_data(cart=cart)

    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Продовжити замовлення", callback_data="action_continue")
    builder.button(text="🛒 Перейти до кошика", callback_data="action_cart")
    builder.adjust(1)

    await callback.message.edit_text(
        f"✅ <b>{drink['name']}</b> додано в кошик!",
        reply_markup=builder.as_markup()
    )


@router.callback_query(lambda c: c.data.startswith("action_"))
async def action_after_add(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "continue":
        await start_order(callback.message, state)
    elif action == "cart":
        await show_cart(callback, state)
    await callback.answer()


# ====================== ДЕСЕРТИ ======================

@router.message(lambda m: m.text == "🍰 Солодощі")
async def show_desserts(message: types.Message):
    builder = InlineKeyboardBuilder()
    for did, d in DESSERTS.items():
        builder.button(text=f"{d['name']} — {d['price']} грн", callback_data=f"dessert_{did}")
    builder.adjust(2)
    await message.answer("🍰 <b>Оберіть солодощі:</b>", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data.startswith("dessert_"))
async def add_dessert(callback: types.CallbackQuery, state: FSMContext):
    dessert_id = callback.data.split("_")[1]
    dessert = DESSERTS.get(dessert_id)
    if not dessert:
        return await callback.answer("❌ Десерт не знайдено")

    data = await state.get_data()
    cart = data.get("cart", {})
    cart.setdefault("desserts", [])
    cart["desserts"].append({
        "id": dessert_id,
        "name": dessert["name"],
        "price": dessert["price"],
        "quantity": 1
    })

    await state.update_data(cart=cart)
    await callback.answer(f"✅ {dessert['name']} додано!")
    await show_cart(callback, state)


# ====================== КОШИК ======================

@router.message(lambda m: m.text == "🛒 Кошик")
async def cart_button(message: types.Message, state: FSMContext):
    await show_cart(message, state)


@router.message(lambda m: m.text == "🔄 Повторити останнє")
async def repeat_last(message: types.Message, state: FSMContext):
    user = get_user_data(message.from_user.id)
    if not user or not user.get("last_order"):
        return await message.answer("😔 У вас ще немає попередніх замовлень")

    await state.update_data(cart=user["last_order"])
    await message.answer("✅ Останнє замовлення завантажено!")
    await show_cart(message, state)


# ====================== ОФОРМЛЕННЯ ЗАМОВЛЕННЯ ======================

@router.callback_query(F.data == "checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    kb = InlineKeyboardBuilder()
    kb.button(text="Самовивіз", callback_data="pickup_Самовивіз")
    kb.button(text="Доставка", callback_data="pickup_Доставка")
    kb.adjust(1)

    await callback.message.edit_text(
        "🚚 <b>Оберіть спосіб отримання:</b>",
        reply_markup=kb.as_markup()
    )
    await state.set_state(OrderStates.choosing_pickup)


@router.callback_query(F.data.startswith("pickup_"))
async def choose_pickup(callback: types.CallbackQuery, state: FSMContext):
    pickup_type = callback.data.split("_")[1]
    await state.update_data(pickup_type=pickup_type)

    if pickup_type == "Доставка":
        await state.set_state(OrderStates.entering_address)
        await callback.message.edit_text("📍 Вкажіть адресу доставки:")
    else:
        await state.update_data(address="м. Київ, вул. Хрещатик, 22")
        await show_order_confirmation(callback, state)


@router.message(OrderStates.entering_address)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 10:
        return await message.answer("❌ Введіть повнішу адресу")
    await state.update_data(address=address)
    await show_order_confirmation(message, state)


async def show_order_confirmation(event, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", {})
    if not cart:
        return await (event.answer if isinstance(event, types.Message) else event.message.edit_text)("❌ Кошик порожній")

    total = calculate_total(cart)
    user = get_user_data(event.from_user.id)
    bonuses = user.get("bonuses", 0)

    text = "<b>📋 Підтвердження замовлення</b>\n\n"
    for d in cart.get("desserts", []):
        qty = d.get("quantity", 1)
        text += f"🍰 {d['name']} ×{qty} — {d['price'] * qty} грн\n"

    for drink_id, items in cart.items():
        if drink_id == "desserts": 
            continue
        drink = MENU.get(drink_id)
        if drink:
            for item in items:
                qty = item.get("quantity", 1)
                text += f"☕ {drink['name']} ×{qty} — {drink['price'] * qty} грн\n"

    text += f"\n━━━━━━━━━━━━━━\n"
    text += f"<b>Спосіб:</b> {data.get('pickup_type')}\n"
    text += f"<b>Адреса:</b> {data.get('address')}\n"
    text += f"🎁 Бонуси: {bonuses} грн\n"
    text += f"<b>Разом: {total} грн</b>"

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Підтвердити", callback_data="confirm_no_bonus")
    if bonuses >= 100:
        kb.button(text="🎟️ Використати бонуси (-50 грн)", callback_data="confirm_with_bonus")
    kb.button(text="❌ Скасувати", callback_data="cancel_order")
    kb.adjust(1)

    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=kb.as_markup())
    else:
        await event.message.edit_text(text, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("confirm_"))
async def final_confirm(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Обробляємо замовлення...")

    data = await state.get_data()
    cart = data.get("cart", {})
    if not cart:
        return await callback.message.edit_text("❌ Кошик порожній")

    use_bonus = callback.data == "confirm_with_bonus"
    if use_bonus:
        spend_bonuses(callback.from_user.id)

    # Формуємо текст товарів
    summary = []
    for d in cart.get("desserts", []):
        summary.append(f"{d.get('name')} (x{d.get('quantity',1)})")
    for drink_id, items in cart.items():
        if drink_id == "desserts": continue
        drink = MENU.get(drink_id)
        if drink:
            for item in items:
                summary.append(f"{drink['name']} (x{item.get('quantity',1)})")

    items_text = ", ".join(summary)
    total_price = calculate_total(cart)
    final_amount = total_price - 50 if use_bonus else total_price

    pickup = data.get("pickup_type", "Самовивіз")
    address = data.get("address", "м. Київ, вул. Хрещатик, 22")

    # Зберігаємо в базу
    order_id = save_order(callback.from_user.id, items_text, final_amount, pickup, address)
    save_last_order(callback.from_user.id, cart)

    # Відправка баристі
    try:
        barista_bot = Bot(
    token=BARISTA_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
        admin_text = f"""🔔 <b>НОВЕ ЗАМОВЛЕННЯ №{order_id}</b>
👤 {callback.from_user.full_name}
📦 {items_text}
💰 {final_amount} грн
📍 {pickup} — {address}"""

        from keyboards import order_control_keyboard
        kb = order_control_keyboard(order_id, callback.from_user.id)

        await barista_bot.send_message(BARISTA_CHAT_ID, admin_text, reply_markup=kb)
    except Exception as e:
        print(f"[BARISTA ERROR]: {e}")

    await callback.message.edit_text(
        f"🎉 <b>Замовлення №{order_id} прийнято!</b>\n\n"
        "Ми вже починаємо готувати вашу каву ❤️\n"
        "Очікуйте повідомлення про готовність!"
    )

    await state.clear()
    await callback.message.answer("Головне меню 👇", reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Скасовано")
    await callback.message.edit_text("❌ Оформлення скасовано.")
    await state.clear()
    await callback.message.answer("Головне меню 👇", reply_markup=main_menu_keyboard())

