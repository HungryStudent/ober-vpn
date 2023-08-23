from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
import database as db
from config_parser import PAY_TOKEN
from create_bot import dp
from keyboards import user as user_kb


@dp.callback_query_handler(text="balance_menu")
async def balance_menu(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    await call.message.answer(f"Ваш баланс: {user['balance']}\n\nВыберите необходимую сумму:",
                              reply_markup=user_kb.balance)
    await call.answer()


@dp.callback_query_handler(user_kb.payment.filter())
async def create_payment(call: CallbackQuery, state: FSMContext, callback_data: dict):
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
    await message.answer(f"Платеж проведен. На ваш аккаунт зачислено {message.successful_payment.total_amount}₽")
