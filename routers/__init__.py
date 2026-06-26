from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .user import router as user_router
from .anchor import router as anchor_router
from .order import router as order_router
from .app import router as app_router

__all__ = ['auth_router', 'dashboard_router', 'user_router', 'anchor_router', 'order_router', 'app_router']
