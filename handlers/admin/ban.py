from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.admin as admin_kb
from states.admin import BanUser
from create_bot import dp


@dp.callback_query_handler(is_admin=True, text="admin_ban", state="*")
async def admin_ban(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Введите user_id")
    await state.set_state(BanUser.user_id)
    await call.answer()


@dp.message_handler(is_admin=True, state=BanUser.user_id)
async def ban_user_menu(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        return await message.answer("Введите корректный user_id")
    if user_id == message.from_user.id:
        return await message.answer("Вы не можете заблокировать себя")
    user = await db.get_user(user_id)
    if user["is_banned"]:
        action = "unban"
        msg = "заблокирован"
    else:
        action = "ban"
        msg = "не заблокирован"
    await message.answer(f"Пользователь {user_id}: {msg}", reply_markup=admin_kb.get_ban(user_id, action))
    await state.finish()


@dp.callback_query_handler(admin_kb.ban_user.filter())
async def ban_user(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = int(callback_data["user_id"])
    action = callback_data["action"]
    if action == "ban":
        status = True
        msg = "Пользователь заблокирован"
    else:
        status = False
        msg = "Пользователь разблокирован"
    await db.set_is_banned(user_id, status)
    await call.message.answer(msg)
    await call.answer()