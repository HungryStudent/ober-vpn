from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

import keyboards.user as user_kb
from create_bot import dp
import database as db


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: Message, state: FSMContext):
    await state.finish()
    user = await db.get_user(message.from_user.id)
    if user is None:
        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    await message.answer("""Приветствие""", reply_markup=user_kb.menu)


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод отменен", reply_markup=user_kb.menu)
