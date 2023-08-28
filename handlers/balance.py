from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

import database as db
from create_bot import dp
from keyboards import user as user_kb
from utils import pay


@dp.callback_query_handler(text="balance_menu")
async def balance_menu(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    await call.message.answer(f"Ваш баланс: {user['balance']}\n\nВыберите необходимую сумму:",
                              reply_markup=user_kb.balance)
    await call.answer()


@dp.callback_query_handler(user_kb.payment.filter())
async def create_payment(call: CallbackQuery, state: FSMContext, callback_data: dict):
    amount = int(callback_data["amount"])
    payment = pay.create_payment(amount, call.from_user.id)
    await call.message.answer("Для оплаты нажмите неа кнопку ниже",
                              reply_markup=user_kb.get_payment_url(payment.confirmation.confirmation_url))
    await call.answer()
