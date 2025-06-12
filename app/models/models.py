from typing import Optional

from sqlalchemy import BigInteger, String, Text, ForeignKey, Index, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import ModelsBase
import sqlalchemy as sa


# Enums
class MessageTypeEnum(sa.Enum):
    TEXT = "text"
    DOCUMENT = "document"


class DocProcessingStatusEnum(sa.Enum):
    PENDING = "pending"
    ANALYZED = "analyzed"
    ERROR = "error"


# Models
class Users(ModelsBase):
    __tablename__ = "users"

    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bot_interaction_created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())

    messages = relationship("Messages", back_populates="sender_user")


class Chats(ModelsBase):
    __tablename__ = "chats"

    chat_title: Mapped[str] = mapped_column(String(255), nullable=False)
    bot_added_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())

    messages = relationship("Messages", back_populates="chat")


class ChatAdmins(ModelsBase):
    __tablename__ = "chat_admins"

    id: None = None

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    first_acknowledged_admin_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())


class ChatSettings(ModelsBase):
    __tablename__ = "chat_settings"

    id: None = None

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    summary_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    settings_updated_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())


class Messages(ModelsBase):
    __tablename__ = "messages"

    telegram_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    sender_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    message_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_type: Mapped[MessageTypeEnum] = mapped_column(sa.String(50), nullable=False,
                                                          default=MessageTypeEnum.TEXT)
    sent_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    summary_id: Mapped[Optional[int]] = mapped_column(ForeignKey("summaries.id"), nullable=True)

    chat = relationship("Chats", back_populates="messages")
    sender_user = relationship("Users", back_populates="messages")
    summary = relationship("Summaries", back_populates="messages")
    document = relationship("Documents", uselist=False, back_populates="message")


class Documents(ModelsBase):
    __tablename__ = "documents"

    document_pk: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    message_fk: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False, unique=True)
    telegram_file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    analysis_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_status: Mapped[DocProcessingStatusEnum] = mapped_column(String(50), nullable=False,
                                                                       default=DocProcessingStatusEnum.PENDING)
    analysis_started_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, nullable=True)
    analysis_completed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, nullable=True)
    document_received_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())

    message = relationship("Messages", back_populates="document")


class Summaries(ModelsBase):
    __tablename__ = "summaries"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())
    summary_content: Mapped[str] = mapped_column(Text, nullable=False)
    messages_since_time: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    messages_until_time: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)

    messages = relationship("Messages", back_populates="summary")
