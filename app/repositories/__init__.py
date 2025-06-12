from .user import UserRepository

__all__ = ("Repositories",)

class Repositories:
    users = UserRepository()
