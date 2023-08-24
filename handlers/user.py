from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.user as user_kb
from config_parser import BOT_NAME
from create_bot import dp


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: Message, state: FSMContext):
    await state.finish()
    user = await db.get_user(message.from_user.id)
    if user is None:
        try:
            inviter_id = int(message.get_args())
        except ValueError:
            inviter_id = None
        else:
            if inviter_id == message.from_user.id:
                inviter_id = None
            else:
                await db.update_user_balance(inviter_id, 50)
                await db.update_user_balance(message.from_user.id, 50)

        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name, inviter_id)
        user = {"balance": 0}
    await message.answer(f"""Приветствие, ваш баланс: {user['balance']}""", reply_markup=user_kb.menu)


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод отменен", reply_markup=user_kb.menu)


@dp.callback_query_handler(text="cancel", state="*")
async def inline_cancel(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Ввод отменен", reply_markup=user_kb.menu)
    await call.answer()


@dp.callback_query_handler(text="ref_menu")
async def ref_menu(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"""Пошлите другу ссылку:

https://t.me/{BOT_NAME}?start={call.from_user.id}

Когда ваш друг зайдет в наш бот по этой ссылке и создаст аккаунт, вы получите 50₽ на баланс!""")
    await call.answer()
