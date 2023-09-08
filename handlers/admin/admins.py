from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, BotCommand, BotCommandScopeChat
from aiogram.utils.exceptions import ChatNotFound

import database as db
import keyboards.admin as admin_kb
from config_parser import ADMINS
from states.admin import ChangeAdmin
from create_bot import dp


@dp.callback_query_handler(is_super_admin=True, text="admins", state="*")
async def admins_menu(call: CallbackQuery, state: FSMContext):
    users = await db.get_users_with_admin()
    msg = "Список админов:\n"
    for user in users:
        msg += f"{user['user_id']} - @{user['username']}"
    await call.message.answer(msg, reply_markup=admin_kb.admins_menu)
    await call.answer()


@dp.callback_query_handler(admin_kb.change_admin.filter())
async def change_admin_start(call: CallbackQuery, state: FSMContext, callback_data: dict):
    action = callback_data["action"]
    await call.message.answer("Введите user_id")
    await state.set_state(ChangeAdmin.user_id)
    await state.update_data(action=action)
    await call.answer()


@dp.message_handler(state=ChangeAdmin.user_id)
async def change_admin(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        return await message.answer("Введите корректный user_id")
    if user_id in ADMINS:
        await message.answer("Невозможно изменить супер-админов")
        return await state.finish()
    data = await state.get_data()
    if data["action"] == "add":
        status = True
        msg = "Админ добавлен"
        commands = [BotCommand(command='/start', description="🏠Главное меню"),
                    BotCommand(command='/devices', description="📱Мои устройства"),
                    BotCommand(command='/topup', description="💵Пополнить баланс"),
                    BotCommand(command='/invite', description="🧍‍♂️Пригласить друга"),
                    BotCommand(command='/admin', description="Админка")]
        try:
            await message.bot.set_my_commands(commands,
                                              scope=BotCommandScopeChat(user_id))
        except ChatNotFound:
            pass
    else:
        status = False
        msg = "Админ удалён"
    await db.set_admin_status(user_id, status)
    await message.answer(msg)
    await state.finish()
