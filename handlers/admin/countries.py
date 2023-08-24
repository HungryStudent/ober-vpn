from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.admin as admin_kb
from create_bot import dp
from states.admin import CreateCountry


@dp.callback_query_handler(is_admin=True, text="admin_countries")
async def admin_countries(call: CallbackQuery):
    countries = await db.get_countries()
    await call.message.edit_text("Меню серверов:", reply_markup=admin_kb.get_countries(countries))


@dp.callback_query_handler(admin_kb.admin_country.filter(), is_admin=True)
async def func(call: CallbackQuery, callback_data: dict):
    country_id = int(callback_data["country_id"])
    country = await db.get_country(country_id)
    servers = await db.get_servers_by_country_id(country_id)
    await call.message.edit_text(country["name"], reply_markup=admin_kb.get_country(country, servers))


@dp.callback_query_handler(text="create_country", is_admin=True)
async def create_country_start(call: CallbackQuery):
    await CreateCountry.name.set()
    await call.message.answer("Введите название страны", reply_markup=admin_kb.cancel)
    await call.answer()


@dp.message_handler(state=CreateCountry.name, is_admin=True)
async def create_country_name(message: Message):
    name = message.text
    country_id = await db.add_country(name)
    country = await db.get_country(country_id)
    servers = await db.get_servers_by_country_id(country_id)
    await message.answer("Страна успешно создана\n\n" + country["name"],
                         reply_markup=admin_kb.get_country(country, servers))
