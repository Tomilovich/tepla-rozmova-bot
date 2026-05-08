from datetime import datetime
import random
from typing import Tuple

from menu import MENU, DESSERTS


# ===== НАЛАШТУВАННЯ ЧАСУ =====
WEEKDAY_OPEN = 8
WEEKDAY_CLOSE = 20

WEEKEND_OPEN = 9
WEEKEND_CLOSE = 19


# ====================== ПРИВІТАННЯ ======================

def get_time_greeting(now: datetime | None = None) -> str:
    now = now or datetime.now()
    hour = now.hour

    if hour < 12:
        return "Доброго ранку"
    elif hour < 18:
        return "Доброго дня"
    return "Доброго вечора"


# ====================== СТАТУС КАВ'ЯРНІ ======================

def get_cafe_status(now: datetime | None = None) -> str:
    now = now or datetime.now()

    if now.weekday() < 5:  # Пн–Пт
        is_open = WEEKDAY_OPEN <= now.hour < WEEKDAY_CLOSE
    else:
        is_open = WEEKEND_OPEN <= now.hour < WEEKEND_CLOSE

    return "🟢 Відкрито" if is_open else "🔴 Зачинено"


# ====================== РЕКОМЕНДАЦІЯ ======================

def get_recommendation(now: datetime | None = None) -> Tuple[str, str]:
    now = now or datetime.now()
    month = now.month

    # ===== СЕЗОННА ЛОГІКА =====
    if month in (11, 12, 1, 2):
        return "latte", "cheesecake"
    elif month in (3, 4, 5):
        return "cappuccino", "croissant"
    elif month in (6, 7, 8):
        return "americano", "muffin"

    # ===== FALLBACK =====
    if not MENU or not DESSERTS:
        return "", ""

    return (
        random.choice(list(MENU.keys())),
        random.choice(list(DESSERTS.keys()))
    )