import asyncio

import database as db
from config_parser import wireguard_price
from create_bot import bot
from keyboards import user as user_kb
import utils.server as server_utils


async def main():
    users = await db.get_users()
    for user in users:
        devices = await db.get_devices_by_user_id_and_device_type(user["user_id"], "wireguard")
        if not devices:
            return
        amount = len(devices) * wireguard_price
        if user["balance"] < amount:
            await db.set_is_wireguard_active(user["user_id"], False)
            await bot.send_message(user["user_id"],
                                   "Недостаточно средств, чтобы оплатить устройства WireGuard. "
                                   "Устройство временно заморожены\nДля активации пополните баланс.",
                                   reply_markup=user_kb.menu)
            for device in devices:
                server = await db.get_server(device["server_id"])
                await server_utils.disable_wireguard_config(server["ip_address"], server["server_password"],
                                                            device["device_id"])


if __name__ == '__main__':
    asyncio.run(main())
