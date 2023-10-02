import asyncio
from datetime import timedelta, datetime

import database as db
import utils.server as server_utils
from config_parser import wireguard_price, outline_prices
from create_bot import bot
from keyboards import user as user_kb


async def main():
    devices = await db.get_devices_expired_sub_time_by_has_auto_renewal(True)
    for device in devices:
        user = await db.get_user(device["user_id"])
        price = 0
        history_msg = "Оплата конфигов"
        if device["device_type"] == "wireguard":
            price = wireguard_price
        elif device["device_type"] == "outline":
            price = outline_prices[device["product_id"]]["price"]
            history_msg = "Оплата ключей"
        if user["balance"] < price:
            server = await db.get_server(device["server_id"])
            await db.set_device_status(device["device_id"], False)
            if device["device_type"] == "wireguard":
                await db.set_is_wireguard_active(user["user_id"], False)
                await server_utils.disable_wireguard_config(server["ip_address"], server["server_password"],
                                                            device["device_id"])
                continue
            elif device["device_type"] == "outline":
                outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
                outline_manager.set_data_limit(device["outline_id"], 0)
                continue
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
            limit = outline_client['dataLimit']['bytes'] // (1000 ** 3) + outline_client_usage
            await db.set_outline_limit(device["device_id"], limit)
            outline_manager.set_data_limit(device["outline_id"], limit)

        await db.update_user_balance(user["user_id"], -price)
        await db.add_history_record(user["user_id"], price, history_msg)

    devices = await db.get_devices_expired_sub_time_by_has_auto_renewal(False)
    for device in devices:
        server = await db.get_server(device["server_id"])
        await db.set_device_status(device["device_id"], False)
        if device["device_type"] == "wireguard":
            await server_utils.disable_wireguard_config(server["ip_address"], server["server_password"],
                                                        device["device_id"])
            continue
        elif device["device_type"] == "outline":
            outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
            outline_manager.set_data_limit(device["outline_id"], 0)
            continue
    #
    # for user in users:
    #     if not user["is_wireguard_active"]:
    #         continue
    #     devices = await db.get_wireguard_devices_for_payment(user["user_id"])
    #     if not devices:
    #         continue
    #     amount = len(devices) * wireguard_price
    #     if user["balance"] < amount:
    #         await db.set_is_wireguard_active(user["user_id"], False)
    #         await bot.send_message(user["user_id"],
    #                                "Недостаточно средств, чтобы оплатить устройства WireGuard. "
    #                                "Устройство временно заморожены\nДля активации пополните баланс.",
    #                                reply_markup=user_kb.show_menu)
    #         for device in devices:
    #             server = await db.get_server(device["server_id"])
    #             await server_utils.disable_wireguard_config(server["ip_address"], server["server_password"],
    #                                                         device["device_id"])
    #     else:
    #         await db.update_user_balance(user["user_id"], -amount)
    #         await db.add_history_record(user["user_id"], amount, "Оплата конфигов")
    #         await db.set_devices_has_first_payment(user["user_id"])
    session = await bot.get_session()
    await session.close()


if __name__ == '__main__':
    asyncio.run(main())
