from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.admin as admin_kb
from states.admin import ChangeBalanceUser
from create_bot import dp


@dp.callback_query_handler(is_admin=True, text="admin_balance", state="*")
async def admin_balance(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Введите user_id", reply_markup=admin_kb.cancel)
    await state.set_state(ChangeBalanceUser.user_id)
    await call.answer()


@dp.message_handler(is_admin=True, state=ChangeBalanceUser.user_id)
async def change_balance_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        return await message.answer("Введите корректный user_id")
    await state.update_data(user_id=user_id)
    await message.answer("Введите сумму")
    await state.set_state(ChangeBalanceUser.amount)


@dp.message_handler(is_admin=True, state=ChangeBalanceUser.amount)
async def change_balance_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        return await message.answer("Введите корректную сумму")
    data = await state.get_data()
    await db.update_user_balance(data["user_id"], amount)
    await message.answer("Баланс изменен", reply_markup=admin_kb.ReplyKeyboardRemove())
    await state.finish()
