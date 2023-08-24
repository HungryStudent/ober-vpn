from aiogram import Bot

import database as db
from config_parser import wireguard_price
from keyboards import user as user_kb
from utils import server as server_utils


async def check_wireguard_active(user_id, bot: Bot):
    user = await db.get_user(user_id)
    if not user["is_wireguard_active"]:
        devices = await db.get_devices_by_user_id_and_device_type(user["user_id"], "wireguard")
        if not devices:
            return await db.set_is_wireguard_active(user_id, True)
        amount = len(devices) * wireguard_price
        if user["balance"] > amount:
            await db.update_user_balance(user_id, -amount)
            for device in devices:
                server = await db.get_server(device["server_id"])
                await server_utils.enable_wireguard_config(server["ip_address"], server["server_password"],
                                                           device["device_id"])
            await bot.send_message(user_id, "Устройства WireGuard оплачены и активированы")
