from __future__ import annotations

from abc import abstractmethod
from typing import Protocol

from sqlalchemy.ext.asyncio import session


__all__ = ["Database", "SessionHandler"]


class Database(Protocol):

    @abstractmethod
    def session(self) -> SessionHandler:
        """Session"""

    @abstractmethod
    def connect(self) -> None:
        """Database connection"""


class SessionHandler(Protocol):

    @abstractmethod
    async def __aenter__(self) -> session.AsyncSession:
        """Context manager"""

    async def __aexit__(self, exception_type: type, exception: Exception, _traceback) -> None:
        """Context manager"""
