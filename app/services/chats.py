from typing import Sequence

from datetime import time as time_type, datetime
from typing import Optional

from aiogram.enums import ContentType
from aiogram.types import Message

from app.models.models import Message as MessageModel
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

    async def add_message(
        self,
        message: Message
    ) -> MessageModel:
        async with ExternalServices.database.session() as session:
            new_message = await Repositories.chats.add_message(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                message_text=message.text,
                message_type=message.content_type,
                sent_at=datetime.now(),
                session=session
            )
            if message.content_type is ContentType.DOCUMENT and message.document is not None:
                if all([message.document.file_name, message.document.mime_type, message.document.file_size]):
                    await Repositories.chats.add_document(
                        message_id=new_message.id,
                        telegram_file_id=message.document.file_id,
                        file_name=message.document.file_name,  # type: ignore
                        file_type=message.document.mime_type,  # type: ignore
                        file_size=message.document.file_size,  # type: ignore
                        session=session
                    )
            await session.commit()
            return new_message

    async def set_summary_time(self, chat_id: int, time: time_type) -> None:
        async with ExternalServices.database.session() as session:
            await Repositories.chats.set_summary_time(chat_id, time, session=session)
