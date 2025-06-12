from app.services.auth import AuthService

__all__ = [
    "Services",
]

class Services:
    auth = AuthService()
