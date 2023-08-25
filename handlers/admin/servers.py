import paramiko
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.admin as admin_kb
from create_bot import dp
from states.admin import CreateServer, ChangeServer
from utils import server as server_utils


@dp.callback_query_handler(admin_kb.admin_server.filter(), is_admin=True)
async def admin_countries(call: CallbackQuery, callback_data: dict):
    server_id = int(callback_data["server_id"])
    server = await db.get_server(server_id)
    await call.message.edit_text(server["ip_address"], reply_markup=admin_kb.get_server(server))


@dp.callback_query_handler(admin_kb.create_server.filter(), is_admin=True)
async def create_server_start(call: CallbackQuery, state: FSMContext, callback_data: dict):
    country_id = int(callback_data["country_id"])
    await state.set_state(CreateServer.ip_address)
    await state.update_data(country_id=country_id)
    await call.message.answer("Введите ip адрес", reply_markup=admin_kb.cancel)
    await call.answer()


@dp.message_handler(state=CreateServer.ip_address, is_admin=True)
async def create_server_ip(message: Message, state: FSMContext):
    ip_address = message.text
    await state.update_data(ip_address=ip_address)
    await message.answer("Введите пароль")
    await state.set_state(CreateServer.server_password)


@dp.message_handler(state=CreateServer.server_password, is_admin=True)
async def create_server_password(message: Message, state: FSMContext):
    password = message.text
    data = await state.get_data()
    ip_address = data["ip_address"]
    country_id = data["country_id"]

    await message.answer("Ожидайте, настраиваем сервер")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=ip_address, password=password, username="root", port=22)
    except paramiko.ssh_exception.AuthenticationException:
        await message.answer("Проблема со входом на сервер, повторите попытку позже")
        await state.finish()
        countries = await db.get_countries()
        return await message.answer("Меню серверов:", reply_markup=admin_kb.get_countries(countries))
    await message.answer("Ожидайте, настраиваем сервер")
    resp = await server_utils.install(ip_address, password)
    if not resp["status"]:
        await message.answer("Проблема со входом на сервер, повторите попытку позже")
        await state.finish()
        countries = await db.get_countries()
        return await message.answer("Меню серверов:", reply_markup=admin_kb.get_countries(countries))
    server = await db.add_server(ip_address, password, resp["outline_url"], resp["outline_sha"], country_id)
    servers = await db.get_servers_by_country_id(country_id)
    if len(servers) == 1:
        await db.set_default_server(country_id, server["server_id"])
    await message.answer("Сервер успешно создан", reply_markup=admin_kb.get_server(server))
    await state.finish()
    #
    #
    # @dp.callback_query_handler(admin_kb.admin_country.filter(), is_admin=True)
    # async def func(call: CallbackQuery, callback_data: dict):
    #     country_id = int(callback_data["country_id"])
    #     country = await db.get_country(country_id)
    #     servers = await db.get_servers_by_country_id(country_id)
    #     await call.message.edit_text(country["name"], reply_markup=admin_kb.get_country(country, servers))
    #
    #


@dp.callback_query_handler(admin_kb.change_server.filter())
async def change_server_start(call: CallbackQuery, state: FSMContext, callback_data: dict):
    server_id = callback_data["server_id"]
    field = callback_data["field"]
    if field == "password":
        await call.message.answer("Введите новый пароль", reply_markup=admin_kb.cancel)
    await state.set_state(ChangeServer.new_value)
    await state.update_data(
        server_id=server_id,
        field=field
    )
    await call.answer()


@dp.message_handler(state=ChangeServer.new_value)
async def change_server_new_value(message: Message, state: FSMContext):
    new_value = message.text
    data = await state.get_data()
    if data["field"] == "password":
        await db.change_server_password(int(data["server_id"]), new_value)
    countries = await db.get_countries()
    await message.answer("Пароль успешно изменён", reply_markup=admin_kb.get_countries(countries))
    await state.finish()


@dp.callback_query_handler(admin_kb.set_default_server.filter())
async def set_default_server(call: CallbackQuery, state: FSMContext, callback_data: dict):
    server_id = int(callback_data["server_id"])
    server = await db.get_server(server_id)
    await db.set_default_server(server["country_id"], server_id)
    await call.message.answer("Сервер установлен как основной")
