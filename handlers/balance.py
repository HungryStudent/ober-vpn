from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

import database as db
from config_parser import wireguard_price
from create_bot import dp
from keyboards import user as user_kb
from utils import pay
from states.user import BalanceAmount


@dp.callback_query_handler(text="balance_menu")
async def balance_menu(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    devices = await db.get_devices_by_user_id_and_device_type(user["user_id"], "wireguard")
    amount = len(devices) * wireguard_price
    try:
        days = float(user["balance"]) // amount
    except ZeroDivisionError:
        days = 0
    await call.message.answer(f"""Баланс: {user['balance']}₽ (~{days} дней)
    
Выберите необходимую сумму:""",
                              reply_markup=user_kb.balance)
    await call.answer()


@dp.callback_query_handler(user_kb.payment.filter())
async def create_payment(call: CallbackQuery, state: FSMContext, callback_data: dict):
    amount = int(callback_data["amount"])
    await call.answer()
    if amount == 0:
        await call.message.answer("Введите сумму (минимум 100 руб.)")
        await state.set_state(BalanceAmount.amount)
        return
    payment = pay.create_payment(amount, call.from_user.id)
    await call.message.answer("Для оплаты нажмите на кнопку ниже",
                              reply_markup=user_kb.get_payment_url(payment.confirmation.confirmation_url))


@dp.message_handler(state=BalanceAmount.amount)
async def balance_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        return await message.answer("Введите целое число!")
    if amount < 100:
        return await message.answer("Минимальная сумма пополнения 100 рублей")

    payment = pay.create_payment(amount, message.from_user.id)
    await message.answer("Для оплаты нажмите на кнопку ниже",
                         reply_markup=user_kb.get_payment_url(payment.confirmation.confirmation_url))
    await state.finish()
