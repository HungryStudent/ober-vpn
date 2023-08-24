import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.admin as admin_kb
from create_bot import dp
from states.admin import CreateCountry, ChangeCountry
from utils import server as server_utils


@dp.message_handler(is_admin=True, commands="devices")
async def get_client_devices(message: Message, state: FSMContext):
    try:
        user_id = int(message.get_args())
    except ValueError:
        return await message.answer("Неверный user_id")
    devices = await db.get_devices_by_user_id(user_id)
    if len(devices) == 0:
        return await message.answer("У данного пользователя нет устройств")
    await message.answer(f"Устройства пользователя {user_id}:", reply_markup=admin_kb.get_devices(devices))


@dp.callback_query_handler(admin_kb.admin_device.filter())
async def admin_device(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    device = await db.get_device(device_id)
    server = await db.get_server(device["server_id"])
    if device["device_type"] == "wireguard":
        await server_utils.get_wireguard_config(server["ip_address"], server["server_password"], device_id)
        await call.message.answer_photo(open(f"u{device_id}.png", "rb"))
        await call.message.answer_document(open(f"u{device_id}.conf", "rb"))
        os.remove(f"u{device_id}.png")
        os.remove(f"u{device_id}.conf")
    elif device["device_type"] == "outline":
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.get_client(device["outline_id"])
        if outline_client is None:
            outline_client = outline_manager.create_client(device["user_id"], 50)
            await db.set_outline_id(device_id, outline_client["id"])
        outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
        usage_gb = outline_client_usage // (1000 ** 3)
        limit_gb = outline_client['dataLimit']['bytes'] // (1000 ** 3)
        await call.message.answer(f"""Использовано {usage_gb}/{limit_gb}ГБ
    {outline_client['accessUrl']}""", reply_markup=admin_kb.get_add_limit(device_id))
    await call.answer()


@dp.callback_query_handler(admin_kb.admin_add_limit.filter())
async def admin_add_limit(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    value = int(callback_data["value"])
    device = await db.get_device(device_id)
    server = await db.get_server(device["server_id"])
    outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
    outline_client = outline_manager.get_client(device["outline_id"])
    outline_manager.set_data_limit(device["outline_id"], outline_client['dataLimit']['bytes'] // (1000 ** 3) + value)
    await call.message.answer("Лимит увеличен")
    await call.answer()