from .routes.customers import router as customers_router
from .routes.orders import router as orders_router
from .routes.analytics import router as analytics_router
from .routes.health import router as health_router

__all__ = ['customers_router', 'orders_router', 'analytics_router', 'health_router'] 