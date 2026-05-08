from .start import router as start_router
from .profile import router as profile_router
from .quiz import router as quiz_router
from .order import router as order_router
from .cart import router as cart_router
from .review import router as review_router

__all__ = ['start_router', 'profile_router', 'quiz_router', 
           'order_router', 'cart_router', 'review_router']