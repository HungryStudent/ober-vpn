import asyncio

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
| balance
| Конфиги\n\n"""

    for i in range(0, len(users), 50):
        curr_users = users[i:i + 50]
        for row in curr_users:
            devices = await db.get_devices_by_user_id_and_device_type(row["user_id"], "wireguard")
            if len(devices) == 0:
                has_wg = "нет"
            else:
                has_wg = "есть"
            devices = await db.get_devices_by_user_id_and_device_type(row["user_id"], "outline")
            if len(devices) == 0:
                has_ol = "нет"
            else:
                has_ol = "есть"

            msg += f"""| {row["username"]}
| {f'<code>{row["user_id"]}</code>'}
| {row["balance"]}
| WG {has_wg}, OL {has_ol}\n\n"""

        await call.message.answer(
            f'<b>Статистика</b>\n\n{msg}')
        await asyncio.sleep(0.1)
        msg = ""
