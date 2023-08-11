from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import keyboards.admin as admin_kb
from states.admin import Mailing
from create_bot import dp
import asyncio


@dp.message_handler(is_admin=True, commands="admin", state="*")
async def admin_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Админ меню", reply_markup=admin_kb.menu)


@dp.callback_query_handler(is_admin=True, text="admin_menu", state="*")
async def call_admin_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Админ меню", reply_markup=admin_kb.menu)
