from aiogram import Router, types, F
from aiogram.enums import ChatType
from app.services import Services

router = Router(name="Add to channel")

@router.my_chat_member(F.chat.type.in_([ChatType.SUPERGROUP, ChatType.GROUP]))
async def check_group_add(message: types.Message):
    await Services.chats.add_chat(
        chat_id=message.chat.id,
        chat_title=message.chat.title or "",
    )
    if not message.from_user:
        return
    admin = await Services.auth.get_or_create_telegram_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await Services.chats.add_admin(
        chat_id=message.chat.id,
        user_id=admin.id,
    )
