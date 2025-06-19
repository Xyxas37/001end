from .base import router as base_router
from .add_transaction import router as add_router
from .stats import router as stats_router
from .setlimit import router as setlimit_router  # <-- добавляем сюда

__all__ = ["base_router", "add_router", "stats_router", "setlimit_router"]
