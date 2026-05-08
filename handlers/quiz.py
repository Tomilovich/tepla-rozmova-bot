from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import QuizStates
from menu import MENU
from database import apply_quiz_discount
from keyboards import inline_kb
from .cart import show_cart

router = Router()


# ====================== СТАРТ КВІЗУ ======================

@router.message(F.text.contains("Вгадай"))
async def start_guess_taste(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(QuizStates.choosing_coffee_type)

    await message.answer(
        "🎯 <b>Вгадай свій ідеальний смак за 3 питання!</b>\n\n"
        "Питання 1/3: Який тип кави ви бажаєте?\n"
        "Міцна чорна чи з молоком?",
        reply_markup=inline_kb(["Міцна чорна", "З молоком"], "q1")
    )


# ====================== ПИТАННЯ 1 ======================

@router.callback_query(lambda c: c.data.startswith("q1_"))
async def quiz_q1(callback: types.CallbackQuery, state: FSMContext):
    ans = callback.data.replace("q1_", "")

    await state.update_data(q1=ans)
    await state.set_state(QuizStates.choosing_sweetness)

    await callback.answer()

    await callback.message.edit_text(
        "Питання 2/3: Чи любите солодкі добавки (сиропи)?",
        reply_markup=inline_kb(["Так", "Ні"], "q2")
    )


# ====================== ПИТАННЯ 2 ======================

@router.callback_query(lambda c: c.data.startswith("q2_"))
async def quiz_q2(callback: types.CallbackQuery, state: FSMContext):
    ans = callback.data.replace("q2_", "")

    await state.update_data(q2=ans)
    await state.set_state(QuizStates.choosing_flavor)

    await callback.answer()

    await callback.message.edit_text(
        "Питання 3/3: Який десертний акцент вам ближче?",
        reply_markup=inline_kb(["Вершковий", "Шоколадний"], "q3")
    )


# ====================== ПИТАННЯ 3 + РЕЗУЛЬТАТ ======================

@router.callback_query(lambda c: c.data.startswith("q3_"))
async def quiz_q3(callback: types.CallbackQuery, state: FSMContext):
    ans = callback.data.replace("q3_", "")

    data = await state.get_data()
    q1 = data.get("q1")
    q2 = data.get("q2")

    # ===== ЛОГІКА ВИБОРУ =====
    if q1 == "Міцна чорна":
        suggested_id = "espresso" if q2 == "Ні" else "raf"
    else:
        suggested_id = "latte" if ans == "Вершковий" else "cappuccino"

    drink = MENU.get(suggested_id)
    if not drink:
        return await callback.answer("❌ Помилка рекомендації")

    # ===== ЗНИЖКА =====
    try:
        apply_quiz_discount(callback.from_user.id)
    except Exception as e:
        print(f"[QUIZ DISCOUNT ERROR]: {e}")

    await state.clear()
    await callback.answer()

    text = (
        f"🎉 <b>Ваш ідеальний смак — {drink['name']}!</b>\n\n"
        f"{drink['desc']}\n"
        f"💰 {drink['price']} грн <b>(-10 грн сьогодні)</b>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Додати в кошик", callback_data=f"qa_{suggested_id}")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())

    # ===== ФОТО =====
    if drink.get("photo"):
        try:
            await callback.bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=drink["photo"],
                caption=drink["name"]
            )
        except Exception as e:
            print(f"[PHOTO ERROR]: {e}")


# ====================== ДОДАТИ З КВІЗУ ======================

@router.callback_query(lambda c: c.data.startswith("qa_"))
async def add_from_quiz(callback: types.CallbackQuery, state: FSMContext):
    drink_id = callback.data.replace("qa_", "")

    drink = MENU.get(drink_id)
    if not drink:
        return await callback.answer("❌ Напій не знайдено")

    data = await state.get_data()
    cart = data.get("cart", {})

    cart.setdefault(drink_id, [])
    cart[drink_id].append({
        "size": "M",
        "milk": "Звичайне коров'яче",
        "syrup": "Без сиропу",
        "shots": 1,
        "quantity": 1
    })

    await state.update_data(cart=cart)

    await callback.answer(f"✅ {drink['name']} додано в кошик!")
    await show_cart(callback, state)