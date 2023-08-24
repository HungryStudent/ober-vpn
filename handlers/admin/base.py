from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.admin as admin_kb
from create_bot import dp


@dp.message_handler(is_admin=True, commands="admin", state="*")
async def admin_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Админ меню", reply_markup=admin_kb.menu)


@dp.callback_query_handler(is_admin=True, text="admin_menu", state="*")
async def call_admin_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Админ меню", reply_markup=admin_kb.menu)


@dp.message_handler(is_admin=True, commands="ban")
async def ban_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.get_args())
    except ValueError:
        return await message.answer("Введите корректный user_id")
    if user_id == message.from_user.id:
        return await message.answer("Вы не можете заблокировать себя")
    await db.set_is_banned(user_id, True)
    await message.answer("Пользователь заблокирован")


@dp.message_handler(is_admin=True, commands="unban")
async def unban_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.get_args())
    except ValueError:
        return await message.answer("Введите корректный user_id")
    await db.set_is_banned(user_id, False)
    await message.answer("Пользователь разблокирован")


@dp.message_handler(is_admin=True, commands="balance")
async def balance_user(message: Message, state: FSMContext):
    try:
        user_id, value = message.get_args().split(" ")
        value = int(value)
        user_id = int(user_id)
    except ValueError:
        return await message.answer("Команда введена неверно. Используйте /balance {id пользователя} {баланс}")
    await db.update_user_balance(user_id, value)
    await message.answer("Баланс изменен")

