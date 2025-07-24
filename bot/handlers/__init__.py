from .start_handler import router as start_router
from .download_handler import router as download_router
from .callback_handler import router as callback_router
from .url_handler import router as url_router

# Список всіх роутерів
routers = [
    start_router,
    url_router,
    download_router,
    callback_router,
]

__all__ = ['routers']