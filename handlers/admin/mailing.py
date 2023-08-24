from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import keyboards.admin as admin_kb
from states.admin import Mailing
from create_bot import dp
import asyncio
import database as db


@dp.callback_query_handler(is_admin=True, text="mailing", state="*")
async def mailing(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Введите сообщение для рассылки")
    await state.set_state(Mailing.text)
    await call.answer()


@dp.message_handler(is_admin=True, state=Mailing.text)
async def mailing_text(message: Message, state: FSMContext):
    await state.update_data(msg_text=message.text)
    await message.answer(f"Вы уверены, что хотите отправить данное сообщение?\n\n{message.text}",
                         reply_markup=admin_kb.mailing)


@dp.callback_query_handler(is_admin=True, state=Mailing.text, text="start_mailing")
async def start_mailing(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_text = data["msg_text"]
    await state.finish()
    users = await db.get_users()
    count = 0
    block_count = 0
    await call.answer()
    for user in users:
        try:
            await call.bot.send_message(user["user_id"], msg_text)
            count += 1
        except:
            block_count += 1
        await asyncio.sleep(0.1)
    await call.message.answer(
        f"Количество получивших сообщение: {count}. Пользователей, заблокировавших бота: {block_count}")


@dp.callback_query_handler(is_admin=True, state=Mailing.text, text="stop_mailing")
async def stop_mailing(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Рассылка отменена")
    await state.finish()
