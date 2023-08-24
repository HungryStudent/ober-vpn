from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from tabulate import tabulate

import keyboards.admin as admin_kb
from states.admin import Mailing, CreateCountry
from create_bot import dp
import asyncio
import database as db


@dp.callback_query_handler(is_admin=True, text="statistics")
async def statistics(call: CallbackQuery):
    await call.message.answer("ДЫВЛАЬ")
    await call.answer()

    users = await db.get_users()
    formatted_users = [
        {
            "username": user["username"],
            "tg_id": user["user_id"],
            "balance": user["balance"]
        }
        for user in users]
    await call.message.answer(
        f'<b>Статистика</b>\n\n<pre>{tabulate(formatted_users, tablefmt="jira", numalign="left")}</pre>')
