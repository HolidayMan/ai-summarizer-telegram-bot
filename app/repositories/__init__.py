from .chats import ChatsRepository
from .user import UserRepository

__all__ = ("Repositories",)

class Repositories:
    users = UserRepository()
    chats = ChatsRepository()
