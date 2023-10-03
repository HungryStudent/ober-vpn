from datetime import datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery

import database as db
from config_parser import wireguard_price, PAY_TOKEN, outline_prices
from create_bot import dp
from keyboards import user as user_kb
from utils import pay
from states.user import BalanceAmount
from utils import server as server_utils


@dp.message_handler(commands="topup", state="*")
async def msg_balance_menu(message: Message, state: FSMContext):
    await state.finish()
    user = await db.get_user(message.from_user.id)
    await message.answer(f"""Баланс: {user['balance']}₽

Выберите необходимую сумму:""",
                         reply_markup=user_kb.balance)


@dp.callback_query_handler(text="balance_menu")
async def balance_menu(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    await call.message.answer(f"""Баланс: {user['balance']}₽
    
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
                              reply_markup=user_kb.get_payment_url(payment.confirmation.confirmation_url, amount))


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
                         reply_markup=user_kb.get_payment_url(payment.confirmation.confirmation_url, amount))
    await state.finish()


@dp.callback_query_handler(user_kb.tg_pay.filter())
async def create_tg_payment(call: CallbackQuery, state: FSMContext, callback_data: dict):
    amount = int(callback_data["amount"])
    await call.bot.send_invoice(call.from_user.id,
                                title="Пополнение баланса",
                                description="Для пополнения баланса перейдите по ссылке: Оплатить",
                                provider_token=PAY_TOKEN,
                                payload="1",
                                currency="RUB",
                                prices=[LabeledPrice(label="Оплата аккаунта", amount=amount * 100)])
    await call.answer()


@dp.pre_checkout_query_handler()
async def approve_order(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types="successful_payment")
async def process_successful_payment(message: Message):
    amount = message.successful_payment.total_amount // 100
    await db.update_user_balance(message.from_user.id, amount)
    user = await db.get_user(message.from_user.id)
    await db.add_history_record(message.from_user.id, amount, "Пополнение")
    await message.answer(f"""Платеж проведен. На Ваш аккаунт зачислено {amount}₽ 

Ваш баланс: {user['balance']}₽""", reply_markup=user_kb.show_menu)
    devices = await db.get_devices_expired_sub_time_by_has_auto_renewal_and_user_id(True, message.from_user.id)
    for device in devices:
        user = await db.get_user(device["user_id"])
        price = 0
        history_msg = "Оплата конфигов"
        if device["device_type"] == "wireguard":
            price = wireguard_price
        elif device["device_type"] == "outline":
            price = outline_prices[device["product_id"]]["price"]
            history_msg = "Оплата ключей"
        if user["balance"] < price:
            server = await db.get_server(device["server_id"])
            await db.set_device_status(device["device_id"], False)
            if device["device_type"] == "wireguard":
                await db.set_is_wireguard_active(user["user_id"], False)
                await server_utils.disable_wireguard_config(server["ip_address"], server["server_password"],
                                                            device["device_id"])
                continue
            elif device["device_type"] == "outline":
                outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
                outline_manager.set_data_limit(device["outline_id"], 0)
                continue
        await db.set_device_status(device["device_id"], True)
        sub_time = datetime.now() + timedelta(days=31)
        await db.set_sub_time(device["device_id"], sub_time)
        server = await db.get_server(device["server_id"])
        if device["device_type"] == "wireguard":
            await server_utils.enable_wireguard_config(server["ip_address"], server["server_password"],
                                                       device["device_id"])
        elif device["device_type"] == "outline":
            outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
            outline_client = outline_manager.get_client(device["outline_id"])
            outline_client_usage = outline_manager.get_usage_data(outline_client["id"]) // (1000 ** 3)
            await db.set_device_outline_traffic(device["device_id"], outline_client_usage)
            limit = outline_client['dataLimit']['bytes'] // (1000 ** 3) + outline_client_usage
            outline_manager.set_data_limit(device["outline_id"], limit)

        await db.update_user_balance(user["user_id"], -price)
        await db.add_history_record(user["user_id"], price, history_msg)
