from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import keyboards.admin as admin_kb
from states.admin import Mailing, CreateCountry
from create_bot import dp
import asyncio
import database as db


@dp.callback_query_handler(admin_kb.admin_server.filter(), is_admin=True)
async def admin_countries(call: CallbackQuery, callback_data: dict):
    server_id = int(callback_data["server_id"])
    server = await db.get_server(server_id)
    await call.message.edit_text(server["ip_address"], reply_markup=admin_kb.get_server(server))
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
# @dp.callback_query_handler(text="create_country", is_admin=True)
# async def create_country_start(call: CallbackQuery):
#     await CreateCountry.name.set()
#     await call.message.answer("Введите название страны", reply_markup=admin_kb.cancel)
#     await call.answer()
#
#
# @dp.message_handler(state=CreateCountry.name, is_admin=True)
# async def create_country_name(message: Message):
#     name = message.text
#     country_id = await db.add_country(name)
#     country = await db.get_country(country_id)
#     servers = await db.get_servers_by_country_id(country_id)
#     await message.answer("Страна успешно создана\n\n" + country["name"],
#                          reply_markup=admin_kb.get_country(country, servers))
