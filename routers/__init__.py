from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .user import router as user_router
from .anchor import router as anchor_router
from .order import router as order_router
from .app_list import router as app_list_router
from .app_config import router as app_config_router
from .media import router as media_router

__all__ = ['auth_router', 'dashboard_router', 'user_router', 'anchor_router', 'order_router', 'app_list_router', 'app_config_router', 'media_router']
    