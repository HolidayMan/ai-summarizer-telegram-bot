from typing import Sequence

from datetime import time as time_type
from app.external_services.external_services import ExternalServices
from app.models.models import Chat, User
from app.repositories import Repositories


class ChatsService:
    async def get_admin_chats(self, admin_id: int) -> Sequence[Chat]:
        async with ExternalServices.database.session() as session:
            chats = await Repositories.chats.get_admins_chats(
                user_id=admin_id,
                session=session
            )
            return chats

    async def add_chat(self, chat_id: int, chat_title: str) -> None:
        async with ExternalServices.database.session() as session:
            await Repositories.chats.create_chat(
                chat_id=chat_id,
                title=chat_title,
                session=session
            )

    async def add_admin(self, chat_id: int, user_id: int) -> None:
        async with ExternalServices.database.session() as session:
            await Repositories.chats.add_chat_admin(
                chat_id=chat_id,
                user_id=user_id,
                session=session
            )

    async def set_summary_time(self, chat_id: int, time: time_type) -> None:
        async with ExternalServices.database.session() as session:
            await Repositories.chats.set_summary_time(chat_id, time, session=session)
