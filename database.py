import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime

DB_NAME = "tepla_rozmova.db"

# ====================== КОНЕКТ ======================
@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR]: {e}")
        raise
    finally:
        conn.close()

# ====================== ІНІЦІАЛІЗАЦІЯ БАЗИ ======================
def init_db():
    """Створює таблиці, якщо їх немає"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                bonuses INTEGER DEFAULT 0,
                favorites TEXT DEFAULT "[]",
                last_order TEXT,
                discount_available INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                items TEXT,
                total_price INTEGER,
                pickup_type TEXT,
                address TEXT,
                status TEXT DEFAULT 'Нове',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                user_id INTEGER,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                comment TEXT,
                created_at TEXT
            );
        """)
    print("✅ База даних ініціалізована")

# ====================== ФУНКЦІЇ ДЛЯ ЗАМОВЛЕНЬ ======================
def save_order(user_id, items, total, p_type, address):
    """Зберігає замовлення та повертає його ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO orders 
            (user_id, items, total_price, pickup_type, address, status) 
            VALUES (?, ?, ?, ?, ?, 'Нове')
            """,
            (user_id, items, total, p_type, address)
        )
        return cursor.lastrowid

def update_order_status(order_id, new_status):
    """Оновлює статус замовлення"""
    with get_connection() as conn:
        conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (new_status, order_id)
        )

# ====================== КОРИСТУВАЧІ ======================
def get_user_data(user_id: int) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()

        if row:
            return {
                "bonuses": row["bonuses"],
                "favorites": json.loads(row["favorites"]),
                "last_order": json.loads(row["last_order"]) if row["last_order"] else None,
                "discount_available": row["discount_available"]
            }

        # Створюємо нового користувача
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        return {"bonuses": 0, "favorites": [], "last_order": None, "discount_available": 0}

# ====================== ОСТАННЄ ЗАМОВЛЕННЯ ======================
def save_last_order(user_id: int, cart: dict):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET last_order=? WHERE user_id=?",
            (json.dumps(cart), user_id)
        )

# ====================== БОНУСИ ======================
def update_bonuses(user_id: int, amount: int):
    user = get_user_data(user_id)
    new_bonuses = user["bonuses"] + (amount // 20)

    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET bonuses=? WHERE user_id=?",
            (new_bonuses, user_id)
        )

def spend_bonuses(user_id: int) -> int:
    """100 балів = 50 грн знижки"""
    user = get_user_data(user_id)
    if user["bonuses"] < 100:
        return 0

    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET bonuses=? WHERE user_id=?",
            (user["bonuses"] - 100, user_id)
        )
    return 50

# ====================== ІНШЕ ======================
def apply_quiz_discount(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET discount_available=10 WHERE user_id=?",
            (user_id,)
        )

def use_discount(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET discount_available=0 WHERE user_id=?",
            (user_id,)
        )