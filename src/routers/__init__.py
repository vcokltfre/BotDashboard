from .dashboard import router as dash_router
from .oauth import router as oauth_router


__all__ = (
    dash_router,
    oauth_router,
)
