from .chats import ChatsRepository
from .documents import DocumentsRepository
from .summaries import SummariesRepository
from .user import UserRepository

__all__ = ("Repositories",)

class Repositories:
    users = UserRepository()
    chats = ChatsRepository()
    documents = DocumentsRepository()
    summaries = SummariesRepository()
