from datetime import datetime, UTC

from aiogram import Router, types, F
from aiogram.enums import ChatType, ContentType

from app.services import Services

router = Router(name="Record all messages")

@router.message(F.chat.type.in_([ChatType.SUPERGROUP, ChatType.GROUP]))
async def record_all_messages(message: types.Message):
    if message.content_type not in [ContentType.TEXT, ContentType.DOCUMENT]:
        return

    await Services.chats.add_message(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        message_text=message.text,
        message_type=message.content_type,
        sent_at=datetime.now()
    )
