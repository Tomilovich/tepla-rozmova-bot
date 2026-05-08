from aiogram.fsm.state import State, StatesGroup


# ====================== ЗАМОВЛЕННЯ ======================

class OrderStates(StatesGroup):
    choosing_category = State()
    choosing_size = State()
    choosing_milk = State()
    choosing_syrup = State()
    choosing_shots = State()

    choosing_pickup = State()
    entering_address = State()


# ====================== КОШИК ======================

class CartStates(StatesGroup):
    editing = State()
    entering_quantity = State()


# ====================== ВІДГУК ======================

class ReviewStates(StatesGroup):
    rating = State()
    comment = State()


# ====================== КВІЗ ======================

class QuizStates(StatesGroup):
    choosing_coffee_type = State()   # q1
    choosing_sweetness = State()     # q2
    choosing_flavor = State()        # q3