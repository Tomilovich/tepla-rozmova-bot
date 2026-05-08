from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto

from config import CAFE_NAME, START_ALBUM
from database import get_user_data
from utils import get_time_greeting, get_cafe_status
from keyboards import main_menu_keyboard

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()

    user = get_user_data(message.from_user.id) or {}
    bonuses = user.get("bonuses", 0)

    name = message.from_user.first_name or "друже"
    greeting = get_time_greeting()
    status = get_cafe_status()

    # ===== ТЕКСТ =====
    caption = (
        f"☕ <b>{greeting}, {name}!</b>\n\n"
        f"Ласкаво просимо до <b>«{CAFE_NAME}»</b> ❤️\n"
        f"Тут кава завжди тепла, а розмова — щира ☕\n\n"
        f"🎁 Ваші бонуси: <b>{bonuses}</b>\n"
        f"📍 Статус: <b>{status}</b>"
    )

    # ===== ФОТО-КАРУСЕЛЬ =====
    if START_ALBUM:
        media = []

        for i, photo_url in enumerate(START_ALBUM):
            try:
                if i == 0:
                    media.append(InputMediaPhoto(media=photo_url, caption=caption))
                else:
                    media.append(InputMediaPhoto(media=photo_url))
            except Exception as e:
                print(f"[PHOTO ERROR]: {e}")

        try:
            await message.answer_media_group(media)
        except Exception as e:
            print(f"[MEDIA GROUP ERROR]: {e}")
            # fallback — якщо не відправилось
            await message.answer(caption)
    else:
        # якщо нема фото
        await message.answer(caption)

    # ===== МЕНЮ =====
    await message.answer(
        "👇 <b>Оберіть дію:</b>",
        reply_markup=main_menu_keyboard()
    )