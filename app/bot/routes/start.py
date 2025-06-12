from aiogram import Router, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.models.models import User as DBUser

router = Router(name="Start")


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext, authorized_user: DBUser | None = None) -> None:
    await state.clear()
    if message.chat.type != enums.ChatType.PRIVATE:
        await message.answer(
            "Hi! I will send summaries every day."
        )
        return
    await message.answer(
        "Welcome! Use /set_time to set the time for daily summaries.\n"
    )
