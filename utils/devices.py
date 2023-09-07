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
            await db.add_history_record(user_id, amount, "Оплата конфигов")
            for device in devices:
                server = await db.get_server(device["server_id"])
                await server_utils.enable_wireguard_config(server["ip_address"], server["server_password"],
                                                           device["device_id"])
            await bot.send_message(user_id, "Устройства WireGuard оплачены и активированы")


async def get_stats_for_menu(user):
    devices = await db.get_devices_by_user_id_and_device_type(user["user_id"], "wireguard")
    amount = len(devices) * wireguard_price
    try:
        days = float(user["balance"]) // amount
    except ZeroDivisionError:
        days = 0
    if user["is_wireguard_active"]:
        wireguard_status = "активен"
        wireguard_desc = ""
    else:
        wireguard_status = "не активен"
        wireguard_desc = "(недостаточно средств)"
    if len(devices) == 0:
        wireguard_status = "не активен"
        wireguard_desc = "(нет конфигов)"

    devices = await db.get_devices_by_user_id_and_device_type(user["user_id"], "outline")
    outline_status = "не активен"
    outline_desc = "(закончился трафик)"
    if len(devices) == 0:
        outline_status = "не активен"
        outline_desc = "(нет ключей)"
    else:
        for device in devices:
            server = await db.get_server(device["server_id"])
            outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
            outline_client = outline_manager.get_client(device["outline_id"])
            outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
            usage_gb = outline_client_usage // (1000 ** 3)
            limit_gb = outline_client['dataLimit']['bytes'] // (1000 ** 3)
            if usage_gb < limit_gb:
                outline_status = "активен"
                outline_desc = ""
                break

    return {
        "days": days, "wireguard_status": wireguard_status, "wireguard_desc": wireguard_desc,
        "outline_status": outline_status, "outline_desc": outline_desc
    }


async def get_stats_by_country(user, country_id):
    devices = await db.get_devices_by_user_id_and_device_type_and_country_id(user["user_id"], "wireguard", country_id)
    amount = len(devices) * wireguard_price
    try:
        days = float(user["balance"]) // amount
    except ZeroDivisionError:
        days = 0
    if user["is_wireguard_active"]:
        wireguard_status = "активен"
        wireguard_desc = ""
    else:
        wireguard_status = "не активен"
        wireguard_desc = "(недостаточно средств)"
    if len(devices) == 0:
        wireguard_status = "не активен"
        wireguard_desc = "(нет конфигов)"

    devices = await db.get_devices_by_user_id_and_device_type_and_country_id(user["user_id"], "outline", country_id)
    outline_status = "не активен"
    outline_desc = "(закончился трафик)"
    if len(devices) == 0:
        outline_status = "не активен"
        outline_desc = "(нет ключей)"
    else:
        for device in devices:
            server = await db.get_server(device["server_id"])
            outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
            outline_client = outline_manager.get_client(device["outline_id"])
            outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
            usage_gb = outline_client_usage // (1000 ** 3)
            limit_gb = outline_client['dataLimit']['bytes'] // (1000 ** 3)
            if usage_gb < limit_gb:
                outline_status = "активен"
                outline_desc = ""
                break

    return {
        "days": days, "wireguard_status": wireguard_status, "wireguard_desc": wireguard_desc,
        "outline_status": outline_status, "outline_desc": outline_desc
    }
