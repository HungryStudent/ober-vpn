from aiogram.types import CallbackQuery
from tabulate import tabulate

import database as db
from create_bot import dp


@dp.callback_query_handler(is_admin=True, text="statistics")
async def statistics(call: CallbackQuery):
    await call.answer()

    users = await db.get_users()

    msg = """<b>Статистика</b>
| username
| tg_id
| balance\n\n"""

    for row in users:
        msg += f"""| {row["username"]}
| {f'<code>{row["user_id"]}</code>'}
| {row["balance"]}\n\n"""

    await call.message.answer(
        f'<b>Статистика</b>\n\n{msg}')
