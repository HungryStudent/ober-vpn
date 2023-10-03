from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, Request

import database as db
from config_parser import wireguard_price, outline_prices
from create_bot import bot
from keyboards import user as user_kb
from utils import server as server_utils

app = FastAPI()


@app.post('/api/pay/yookassa')
async def yookassa_request(request: Request):
    data = await request.json()
    amount = int(float(data["object"]["amount"]["value"]))
    user_id = int(float(data["object"]["metadata"]["user_id"]))
    await db.update_user_balance(user_id, amount)
    user = await db.get_user(user_id)
    await db.add_history_record(user_id, amount, "Пополнение")
    await bot.send_message(user_id, f"""Платеж проведен. На Ваш аккаунт зачислено {amount}₽ 

Ваш баланс: {user['balance']}₽""", reply_markup=user_kb.show_menu)
    # await check_wireguard_active(user_id, bot)
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
            outline_manager.set_data_limit(device["outline_id"], limit)

        await db.update_user_balance(user["user_id"], -price)
        await db.add_history_record(user["user_id"], price, history_msg)
    return 200


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
