from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import get_user_data
from menu import MENU, DESSERTS
from keyboards import main_menu_keyboard
from .cart import show_cart
from utils import get_recommendation

router = Router()


# ====================== БОНУСИ ======================
@router.message(F.text == "🎁 Бонуси")
async def show_bonuses(message: types.Message):
    user = get_user_data(message.from_user.id) or {}
    bonuses = user.get("bonuses", 0)
    discount = user.get("discount_available", 0)

    text = (
        "🎁 <b>Ваш профіль бонусів</b>\n\n"
        f"💰 Бонусні бали: <b>{bonuses}</b>\n"
        f"🎟️ Знижка: <b>{discount} грн</b>\n\n"
        "📌 100 балів = 50 грн знижки"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


# ====================== УЛЮБЛЕНІ ======================
@router.message(F.text == "❤️ Улюблені")
async def show_favorites(message: types.Message):
    user = get_user_data(message.from_user.id) or {}
    favorites = user.get("favorites", [])

    if not favorites:
        await message.answer(
            "❤️ <b>У вас поки немає улюблених напоїв</b>\n\n"
            "Замовте щось смачне ☕",
            reply_markup=main_menu_keyboard()
        )
        return

    text = "❤️ <b>Ваші улюблені напої:</b>\n\n"
    builder = InlineKeyboardBuilder()
    for drink_name in favorites:
        drink_id = next((pid for pid, d in MENU.items() if d["name"] == drink_name), None)
        if not drink_id:
            continue
        text += f"☕ {drink_name}\n"
        builder.button(text=f"➕ {drink_name}", callback_data=f"addfav_{drink_id}")

    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup())


# ====================== ДОДАТИ З УЛЮБЛЕНИХ ======================
@router.callback_query(lambda c: c.data.startswith("addfav_"))
async def add_from_favorite(callback: types.CallbackQuery, state: FSMContext):
    drink_id = callback.data.replace("addfav_", "")
    drink = MENU.get(drink_id)
    if not drink:
        return await callback.answer("❌ Напій не знайдено")

    data = await state.get_data()
    cart = data.get("cart", {})
    cart.setdefault(drink_id, []).append({
        "size": "M",
        "milk": "Звичайне коров'яче",
        "syrup": "Без сиропу",
        "shots": 1,
        "quantity": 1
    })

    await state.update_data(cart=cart)
    await callback.answer(f"✅ {drink['name']} додано!")
    await show_cart(callback, state)


# ====================== РЕКОМЕНДАЦІЯ ======================
@router.message(F.text == "🌟 Рекомендація")
async def show_recommendation(message: types.Message):
    drink_id, dessert_id = get_recommendation()
    drink = MENU.get(drink_id)
    dessert = DESSERTS.get(dessert_id)

    if not drink or not dessert:
        return await message.answer("❌ Помилка рекомендації")

    text = (
        "🌟 <b>Сьогодні рекомендуємо:</b>\n\n"
        f"☕ {drink['name']} — {drink['price']} грн\n"
        f"🍰 {dessert['name']} — {dessert['price']} грн"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


