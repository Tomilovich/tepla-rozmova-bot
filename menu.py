from typing import Dict, List

# ===== ДЕФОЛТНЕ ФОТО =====
DEFAULT_PHOTO = "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg"


# ===== ФОТО =====
ITEM_PHOTOS: Dict[str, str] = {
    "espresso": "https://images.pexels.com/photos/14704904/pexels-photo-14704904.jpeg",
    "americano": "https://images.pexels.com/photos/33856911/pexels-photo-33856911.jpeg",
    "cappuccino": "https://images.pexels.com/photos/28496565/pexels-photo-28496565.jpeg",
    "latte": "https://images.pexels.com/photos/14704656/pexels-photo-14704656.jpeg",
    "flatwhite": "https://images.pexels.com/photos/350478/pexels-photo-350478.jpeg",
    "raf": "https://images.pexels.com/photos/14704662/pexels-photo-14704662.jpeg",

    "croissant": "https://images.pexels.com/photos/12176271/pexels-photo-12176271.jpeg",
    "cheesecake": "https://images.pexels.com/photos/24206897/pexels-photo-24206897.jpeg",
    "brownie": "https://images.pexels.com/photos/2955818/pexels-photo-2955818.jpeg",
    "muffin": "https://images.pexels.com/photos/6783155/pexels-photo-6783155.jpeg",
    "tiramisu": "https://images.pexels.com/photos/33215789/pexels-photo-33215789.jpeg",
}


# ===== МЕНЮ =====
MENU: Dict[str, dict] = {
    "espresso": {"name": "Еспресо", "price": 55, "desc": "Класичний міцний еспресо", "time": "3-4 хв"},
    "americano": {"name": "Американо", "price": 65, "desc": "Еспресо з водою", "time": "4 хв"},
    "cappuccino": {"name": "Капучино", "price": 75, "desc": "З молочною піною", "time": "5-6 хв"},
    "latte": {"name": "Латте", "price": 80, "desc": "Ніжний молочний напій", "time": "5-6 хв"},
    "flatwhite": {"name": "Флет Уайт", "price": 78, "desc": "Оксамитовий смак", "time": "5 хв"},
    "raf": {"name": "Раф", "price": 85, "desc": "Вершковий ванільний напій", "time": "6 хв"},
}


# ===== ДЕСЕРТИ =====
DESSERTS: Dict[str, dict] = {
    "croissant": {"name": "Круасан", "price": 65, "desc": "Вершковий круасан", "time": "2 хв"},
    "cheesecake": {"name": "Чізкейк", "price": 95, "desc": "Класичний чізкейк", "time": "1 хв"},
    "brownie": {"name": "Брауні", "price": 75, "desc": "Шоколадний десерт", "time": "1 хв"},
    "muffin": {"name": "Мафін", "price": 60, "desc": "З шоколадом", "time": "1 хв"},
    "tiramisu": {"name": "Тірамісу", "price": 85, "desc": "Італійський десерт", "time": "2 хв"},
}


# ===== ДОДАЄМО ФОТО БЕЗПЕЧНО =====
def attach_photos(data: Dict[str, dict]):
    for key, item in data.items():
        item["photo"] = ITEM_PHOTOS.get(key, DEFAULT_PHOTO)


attach_photos(MENU)
attach_photos(DESSERTS)


# ===== НАЛАШТУВАННЯ =====
SIZES: List[str] = ["S", "M", "L"]

MILKS: List[str] = [
    "Звичайне коров'яче",
    "Вівсяне",
    "Мигдальне",
    "Кокосове",
    "Безлактозне"
]

SYRUPS: List[str] = [
    "Без сиропу",
    "Ваніль",
    "Карамель",
    "Шоколад",
    "Мигдаль"
]

SHOTS: List[int] = [1, 2, 3]