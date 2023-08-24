from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import keyboards.admin as admin_kb
from states.admin import Mailing
from create_bot import dp
import asyncio
import database as db

@dp.message_handler(is_admin=True, commands="admin", state="*")
async def admin_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Админ меню", reply_markup=admin_kb.menu)


@dp.callback_query_handler(is_admin=True, text="admin_menu", state="*")
async def call_admin_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Админ меню", reply_markup=admin_kb.menu)


@dp.message_handler(commands="ban")
async def ban_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.get_args())
    except ValueError:
        return await message.answer("Введите корректный user_id")
    if user_id == message.from_user.id:
        return await message.answer("Вы не можете заблокировать себя")
    await db.set_is_banned(user_id, True)
    await message.answer("Пользователь заблокирован")


@dp.message_handler(commands="unban")
async def ban_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.get_args())
    except ValueError:
        return await message.answer("Введите корректный user_id")
    await db.set_is_banned(user_id, False)
    await message.answer("Пользователь разблокирован")