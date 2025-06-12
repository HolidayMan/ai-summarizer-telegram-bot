from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from app.services import Services


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message | types.CallbackQuery, data):
        data["authorized_user"] = await Services.auth.get_or_create_telegram_user(
            telegram_id=event.from_user.id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name
        )
        return await handler(event, data)
