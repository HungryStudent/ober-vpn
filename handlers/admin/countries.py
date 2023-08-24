from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.admin as admin_kb
from create_bot import dp
from states.admin import CreateCountry, ChangeCountry


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
async def create_country_name(message: Message, state: FSMContext):
    name = message.text
    country_id = await db.add_country(name)
    country = await db.get_country(country_id)
    servers = await db.get_servers_by_country_id(country_id)
    await message.answer("Страна успешно создана\n\n" + country["name"],
                         reply_markup=admin_kb.get_country(country, servers))
    await state.finish()


@dp.callback_query_handler(admin_kb.change_country.filter())
async def change_country_start(call: CallbackQuery, state: FSMContext, callback_data: dict):
    country_id = callback_data["country_id"]
    field = callback_data["field"]
    if field == "name":
        await call.message.answer("Введите новое название страны")
    await state.set_state(ChangeCountry.new_value)
    await state.update_data(
        country_id=country_id,
        field=field
    )
    await call.answer()


@dp.message_handler(state=ChangeCountry.new_value)
async def change_country_new_value(message: Message, state: FSMContext):
    new_value = message.text
    data = await state.get_data()
    if data["field"] == "name":
        await db.change_country_name(int(data["country_id"]), new_value)
    countries = await db.get_countries()
    await message.answer("название успешно изменено", reply_markup=admin_kb.get_countries(countries))
    await state.finish()


@dp.callback_query_handler(admin_kb.delete_country.filter())
async def delete_country(call: CallbackQuery, state: FSMContext, callback_data: dict):
    country_id = int(callback_data["country_id"])
    servers = await db.get_servers_by_country_id(country_id)
    if len(servers) != 0:
        await call.message.answer("В стране есть сервера!")
    else:
        await db.delete_country(country_id)
        await call.message.edit_text("Страна удалена")
    await call.answer()
