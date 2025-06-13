from enum import Enum
from typing import Optional
from uuid import UUID

from aiogram.enums import ContentType
from sqlalchemy import BigInteger, String, Text, ForeignKey, Index, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, time
from app.models.base import ModelsBase
import sqlalchemy as sa


# Enums
class DocProcessingStatusEnum(Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    ANALYZED = "analyzed"
    ERROR = "error"


# Models
class User(ModelsBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)  # Telegram user ID
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Telegram username (handle)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bot_interaction_created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())

    messages = relationship("Message", back_populates="sender_user")


class Chat(ModelsBase):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)  # Telegram chat ID
    chat_title: Mapped[str] = mapped_column(String(255), nullable=False)
    bot_added_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())

    messages = relationship("Message", back_populates="chat")


class ChatAdmin(ModelsBase):
    __tablename__ = "chat_admins"

    id: None = None

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    first_acknowledged_admin_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())


class ChatSettings(ModelsBase):
    __tablename__ = "chat_settings"

    id: None = None

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    summary_time: Mapped[time] = mapped_column(Time, nullable=False)


class Message(ModelsBase):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    sender_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    message_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_type: Mapped[ContentType] = mapped_column(sa.String(50), nullable=False,
                                                          default=ContentType.TEXT)
    sent_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    summary_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("summaries.id"), nullable=True)

    chat = relationship("Chat", back_populates="messages")
    sender_user = relationship("User", back_populates="messages")
    summary = relationship("Summary", back_populates="messages")
    documents = relationship("Document", uselist=False, back_populates="message")


class Document(ModelsBase):
    __tablename__ = "documents"

    message_fk: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False)
    telegram_file_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    analysis_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_status: Mapped[DocProcessingStatusEnum] = mapped_column(String(50), nullable=False,
                                                                       default=DocProcessingStatusEnum.NOT_STARTED.value)
    analysis_started_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, nullable=True)
    analysis_completed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, nullable=True)

    message = relationship("Message", back_populates="documents")


class Summary(ModelsBase):
    __tablename__ = "summaries"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())
    summary_content: Mapped[str] = mapped_column(Text, nullable=False)
    messages_since_time: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    messages_until_time: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)

    messages = relationship("Message", back_populates="summary")
