from aiogram import Bot
from datetime import datetime, timedelta
import database as db
from config_parser import wireguard_price, outline_prices
from utils import server as server_utils


def get_days_text(n):
    if n in (11, 12, 13, 14):
        return 'дней'
    elif n % 10 == 1:
        return 'день'
    elif n % 10 in (2, 3, 4):
        return 'дня'
    else:
        return 'дней'


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
    devices_stat = await db.get_devices_stat_wg(user["user_id"])
    wireguard_status = "активен"
    wireguard_desc = ""
    if devices_stat["all_devices"] == 0:
        wireguard_status = "не активен"
        wireguard_desc = "(нет конфигов)"
    elif devices_stat["no_sub_auto_renewal"] > 0 and devices_stat["sub"] > 0:
        wireguard_status = "частично активен"
        wireguard_desc = "(Недостаточно баланса для продления некоторых устройств)"
    elif devices_stat["no_sub"] > 0 and devices_stat["sub"] > 0:
        wireguard_status = "частично активен"
        wireguard_desc = "(Подробнее в «Мои устройства»)"
    elif devices_stat["no_sub"] > 0 and devices_stat["sub"] == 0:
        wireguard_status = "не активен"
        wireguard_desc = "(Подробнее в «Мои устройства»)"

    devices = await db.get_devices_by_user_id_and_device_type(user["user_id"], "outline")
    outline_status = "активен"
    outline_desc = ""
    if len(devices) == 0:
        outline_status = "не активен"
        outline_desc = "(нет ключей)"
    else:
        no_sub_auto_renewal = 0
        no_sub_no_auto_renewal = 0
        no_sub = 0
        sub = 0
        for device in devices:
            server = await db.get_server(device["server_id"])
            outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
            outline_client = outline_manager.get_client(device["outline_id"])
            if outline_client is None:
                outline_client_usage = device["outline_limit"]
            else:
                outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
            usage_gb = outline_client_usage // (1000 ** 3)
            limit_gb = device["outline_limit"]
            is_active = usage_gb < limit_gb or device["sub_time"] > datetime.now()
            if not is_active and device["has_auto_renewal"]:
                no_sub_auto_renewal += 1
            elif is_active:
                sub += 1
            elif not is_active and not device["has_auto_renewal"]:
                no_sub_no_auto_renewal += 1
            elif not is_active:
                no_sub += 1
        if no_sub_auto_renewal > 0 and sub > 0:
            wireguard_status = "частично активен"
            wireguard_desc = "(Недостаточно баланса для продления некоторых устройств)"
        elif no_sub > 0 and sub > 0:
            wireguard_status = "частично активен"
            wireguard_desc = "(Подробнее в «Мои устройства»)"
        elif no_sub > 0 and sub == 0:
            wireguard_status = "не активен"
            wireguard_desc = "(Подробнее в «Мои устройства»)"

    return {
        "wireguard_status": wireguard_status, "wireguard_desc": wireguard_desc,
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
            if outline_client is None:
                outline_client_usage = device["outline_limit"]
            else:
                outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
            usage_gb = outline_client_usage // (1000 ** 3)
            limit_gb = device["outline_limit"]
            if usage_gb < limit_gb:
                outline_status = "активен"
                outline_desc = ""
                break

    return {
        "days": days, "wireguard_status": wireguard_status, "wireguard_desc": wireguard_desc,
        "outline_status": outline_status, "outline_desc": outline_desc
    }


async def get_stats_by_server(user, server_id):
    devices = await db.get_devices_by_user_id_and_device_type_and_server_id(user["user_id"], "wireguard", server_id)
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

    devices = await db.get_devices_by_user_id_and_device_type_and_server_id(user["user_id"], "outline", server_id)
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
            if outline_client is None:
                outline_client_usage = device["outline_limit"]
            else:
                outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
            usage_gb = outline_client_usage // (1000 ** 3)
            limit_gb = device["outline_limit"]
            if usage_gb < limit_gb:
                outline_status = "активен"
                outline_desc = ""
                break

    return {
        "days": days, "wireguard_status": wireguard_status, "wireguard_desc": wireguard_desc,
        "outline_status": outline_status, "outline_desc": outline_desc
    }


async def get_outline_gb(device_id):
    device = await db.get_device(device_id)
    server = await db.get_server(device["server_id"])
    outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
    outline_client = outline_manager.get_client(device["outline_id"])
    outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
    usage_gb = outline_client_usage // (1000 ** 3) - device["outline_traffic"]


async def check_after_change_balance(user_id):
    devices = await db.get_devices_expired_sub_time_by_has_auto_renewal_and_user_id(True, user_id)
    for device in devices:
        user = await db.get_user(device["user_id"])
        price = 0
        history_msg = "Оплата конфигов"
        if device["device_type"] == "wireguard":
            price = wireguard_price
        elif device["device_type"] == "outline":
            price = outline_prices[device["product_id"]]["price"]
            history_msg = "Оплата ключей"
        if user["balance"] >= price:
            await db.set_device_status(device["device_id"], True)
            sub_time = datetime.now() + timedelta(days=31)
            await db.set_sub_time(device["device_id"], sub_time)
            server = await db.get_server(device["server_id"])
            if device["device_type"] == "wireguard":
                await server_utils.enable_wireguard_config(server["ip_address"], server["server_password"],
                                                           device["device_id"])
            elif device["device_type"] == "outline":
                outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
                outline_client = outline_manager.get_client(device["outline_id"])
                outline_client_usage = outline_manager.get_usage_data(outline_client["id"]) // (1000 ** 3)
                await db.set_device_outline_traffic(device["device_id"], outline_client_usage)
                limit = device["outline_limit"] + outline_client_usage
                outline_manager.set_data_limit(device["outline_id"], limit)

            await db.update_user_balance(user["user_id"], -price)
            await db.add_history_record(user["user_id"], price, history_msg)
