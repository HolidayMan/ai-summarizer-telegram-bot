from app.services.auth import AuthService
from app.services.chats import ChatsService

__all__ = [
    "Services",
]


class Services:
    auth = AuthService()
    chats = ChatsService()
