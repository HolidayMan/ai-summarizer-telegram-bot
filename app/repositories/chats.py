from datetime import time
from datetime import datetime
from typing import Sequence

from aiogram.enums import ContentType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.models import Chat, ChatAdmin, ChatSettings, Message, Document


class ChatsRepository:
    async def create_chat(self, chat_id: int, title: str, session: AsyncSession) -> Chat:
        # Create the chat
        new_chat = Chat(
            id=chat_id,
            chat_title=title,
            bot_added_at=datetime.utcnow()
        )
        session.add(new_chat)

        new_chat_settings = ChatSettings(
            chat_id=chat_id,
            summary_time=time(hour=19),
        )
        session.add(new_chat_settings)
        try:
            await session.commit()
            return new_chat
        except IntegrityError:
            await session.rollback()
            raise ValueError("Chat with this ID already exists")

    async def get_chat(self, chat_id: int, session: AsyncSession) -> Chat | None:
        query = select(Chat).where(Chat.id == chat_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_admins_chats(self, user_id: int, session: AsyncSession) -> Sequence[Chat]:
        # Join Chat and ChatAdmin tables to get all chats where the user is an admin
        query = select(Chat).join(
            ChatAdmin, ChatAdmin.chat_id == Chat.id
        ).where(
            ChatAdmin.user_id == user_id
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def add_chat_admin(self, chat_id: int, user_id: int, session: AsyncSession) -> ChatAdmin:
        chat_admin = ChatAdmin(
            user_id=user_id,
            chat_id=chat_id,
            first_acknowledged_admin_at=datetime.utcnow()
        )
        session.add(chat_admin)

        try:
            await session.commit()
            return chat_admin
        except IntegrityError:
            await session.rollback()
            raise ValueError("User is already an admin for this chat or references are invalid")

    async def remove_chat_admin(self, chat_id: int, user_id: int, session: AsyncSession) -> bool:
        query = select(ChatAdmin).where(
            ChatAdmin.chat_id == chat_id,
            ChatAdmin.user_id == user_id
        )
        result = await session.execute(query)
        chat_admin = result.scalars().first()

        if not chat_admin:
            return False

        await session.delete(chat_admin)
        await session.commit()
        return True

    async def is_chat_admin(self, chat_id: int, user_id: int, session: AsyncSession) -> bool:
        query = select(ChatAdmin).where(
            ChatAdmin.chat_id == chat_id,
            ChatAdmin.user_id == user_id
        )
        result = await session.execute(query)
        return result.scalars().first() is not None

    async def update_chat_title(self, chat_id: int, title: str, session: AsyncSession) -> bool:
        chat = await self.get_chat(chat_id, session)
        if not chat:
            return False

        chat.chat_title = title
        await session.commit()
        return True

    async def add_message(
        self,
        chat_id: int,
        user_id: int,
        message_text: str | None,
        message_type: ContentType,
        sent_at: datetime,
        session: AsyncSession
    ) -> Message:
        if sent_at is None:
            sent_at = datetime.utcnow()
            
        message = Message(
            chat_id=chat_id,
            sender_user_id=user_id,
            message_text=message_text,
            message_type=message_type,
            sent_at=sent_at
        )
        
        session.add(message)
        await session.flush()
        return message

    async def set_summary_time(self, chat_id: int, time: time, session: AsyncSession) -> None:
        query = select(ChatSettings).where(ChatSettings.chat_id == chat_id)
        result = await session.execute(query)
        settings = result.scalars().first()
        if not settings:
            settings = ChatSettings(chat_id=chat_id, summary_time=time)
            session.add(settings)
        else:
            settings.summary_time = time
        await session.commit()

    async def add_document(self, message_id: int, telegram_file_id: str,
                           file_name: str, file_type: str, file_size: int, session: AsyncSession) -> Document:
        document = Document(
            message_fk=message_id,
            telegram_file_id=telegram_file_id,
            file_name=file_name,
            file_type=file_type,
            file_size_bytes=file_size
        )
        session.add(document)
        await session.flush()
        return document

