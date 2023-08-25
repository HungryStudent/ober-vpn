from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tabulate import tabulate

import database as db
import keyboards.user as user_kb
from config_parser import BOT_NAME, wireguard_price
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
                await db.add_history_record(inviter_id, 50, "Реферальный бонус")
                await db.update_user_balance(message.from_user.id, 50)
                await db.add_history_record(message.from_user.id, 50, "Реферальный бонус")
        user = await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                                 inviter_id)
    devices = await db.get_devices_by_user_id_and_device_type(user["user_id"], "wireguard")
    amount = len(devices) * wireguard_price
    days = float(user["balance"]) // amount
    await message.answer(f"""Приветствие, ваш баланс: {user['balance']}₽ (~{days} дней)""", reply_markup=user_kb.menu)


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


@dp.callback_query_handler(state="*", text="history")
async def history(call: CallbackQuery, state: FSMContext):
    history = await db.get_history_by_user_id(call.from_user.id)
    formatted_history = [
        {
            "datetime": row["datetime"],
            "amount": row["amount"],
            "msg": row["msg"]
        }
        for row in history]
    formatted_history.insert(0, {"datetime": "Дата", "amount": "₽", "msg": "ТИП"})
    await call.message.answer(
        f'<b>Статистика</b>\n\n<pre>{tabulate(formatted_history, tablefmt="jira", numalign="left")}</pre>')
    await call.answer()
