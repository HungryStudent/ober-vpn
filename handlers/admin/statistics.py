from aiogram.types import CallbackQuery
from tabulate import tabulate

import database as db
from create_bot import dp


@dp.callback_query_handler(is_admin=True, text="statistics")
async def statistics(call: CallbackQuery):
    await call.answer()

    users = await db.get_users()
    formatted_users = [
        {
            "username": user["username"],
            "tg_id": f'<code>{user["user_id"]}</code>',
            "balance": user["balance"]
        }
        for user in users]
    await call.message.answer(
        f'<b>Статистика</b>\n\n{tabulate(formatted_users, tablefmt="jira", numalign="left")}')
