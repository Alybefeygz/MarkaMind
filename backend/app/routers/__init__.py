from .auth import router as auth_router
from .brands import router as brands_router
from .stores import router as stores_router
from .chatbots import router as chatbots_router
from .knowledge import router as knowledge_router
from .conversations import router as conversations_router
from .uploads import router as uploads_router
from .widget import router as widget_router
from .feedback import router as feedback_router

__all__ = [
    "auth_router",
    "brands_router",
    "stores_router",
    "chatbots_router",
    "knowledge_router",
    "conversations_router",
    "uploads_router",
    "widget_router",
    "feedback_router"
]