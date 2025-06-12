from datetime import time

from aiogram import Router, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.models.models import User as DBUser
from aiogram.fsm.state import State, StatesGroup
from app.services import Services

class SetTimeState(StatesGroup):
    choose_chat = State()
    set_time = State()


router = Router(name="Set time")


@router.message(Command("set_time"))
async def start(message: types.Message, state: FSMContext, authorized_user: DBUser) -> None:
    if message.chat.type != enums.ChatType.PRIVATE:
        return
    await state.clear()
    chats = await Services.chats.get_admin_chats(authorized_user.id)
    if not chats:
        await message.answer(
            "You have no chats to set time for. Please add the bot to any chat where you are admin."
        )
        return
    keyboard_builder = ReplyKeyboardBuilder()
    for chat in chats:
        keyboard_builder.add(types.KeyboardButton(text=f"{chat.chat_title} ({chat.id})"))
    markup = keyboard_builder.as_markup(reply_markup=ReplyKeyboardRemove(), resize_keyboard=True)
    await message.answer(
        "Please select a chat to set the time for daily summaries:",
        reply_markup=markup
    )
    await state.set_state(SetTimeState.choose_chat)


@router.message(SetTimeState.choose_chat)
async def choose_chat(message: types.Message, state: FSMContext) -> None:
    try:
        chat_id = message.text.split()[-1].strip("()")
        print(chat_id)
        await state.update_data(chat_id=int(chat_id))
    except ValueError:
        await message.answer("Invalid chat ID. Please try again. /set_time", reply_markup=ReplyKeyboardRemove())
        return
    await message.answer("Please enter the time for daily summaries (e.g. 19:00):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SetTimeState.set_time)


@router.message(SetTimeState.set_time)
async def set_time(message: types.Message, state: FSMContext) -> None:
    try:
        await state.update_data(time=time.fromisoformat(message.text))
    except ValueError:
        await message.answer("Invalid time format. Please try again. /set_time")
        return
    data = await state.get_data()
    await Services.chats.set_summary_time(data["chat_id"], data["time"])
    await message.answer("Time for daily summaries has been set successfully.")
    await state.clear()

