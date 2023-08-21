from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from states.user import NewDevice
import keyboards.user as user_kb
from create_bot import dp
import database as db
from utils import server as server_utils


@dp.callback_query_handler(text="devices")
async def devices_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    devices = await db.get_devices_by_user_id(call.from_user.id)
    await call.message.answer("Ваши устройства", reply_markup=user_kb.get_devices(devices))
    await call.answer()


@dp.callback_query_handler(text="new_device")
async def new_device_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Выберите тип:", reply_markup=user_kb.choose_device_type)
    await state.set_state(NewDevice.device_type)
    await call.answer()


@dp.callback_query_handler(state=NewDevice.device_type)
async def new_device_device_type(call: CallbackQuery, state: FSMContext):
    await state.update_data(device_type=call.data)
    await state.set_state(NewDevice.name)
    await call.message.edit_text("Введите название устройства", reply_markup=user_kb.inline_cancel)


@dp.message_handler(state=NewDevice.name)
async def new_device_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(NewDevice.country)
    countries = await db.get_countries_for_new_device()
    await message.answer("Выберите страну", reply_markup=user_kb.get_countries(countries))


@dp.callback_query_handler(user_kb.new_device_country.filter(), state=NewDevice.country)
async def new_device_country(call: CallbackQuery, state: FSMContext, callback_data: dict):
    data = await state.get_data()
    country_id = int(callback_data["country_id"])
    server = await db.get_current_server_by_country_id(country_id)
    await db.add_new_device(call.from_user.id, data["device_type"], data["name"], server["server_id"])
    await call.message.edit_text("Девайс успешно создан")
    if data["device_type"] == "wireguard":
        await server_utils.create_wireguard_config(server["ip_address"], server["server_password"], call.from_user.id)
        await call.message.answer_photo(open(f"{call.from_user.id}.png", "rb"))
        await call.message.answer_document(open(f"{call.from_user.id}.conf", "rb"))

