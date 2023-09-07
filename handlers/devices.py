import os
from datetime import date

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.user as user_kb
from config_parser import outline_prices
from create_bot import dp
from states.user import NewDevice
from utils import server as server_utils
from utils.devices import check_wireguard_active

instructions = {
    "wireguard": """Инструкция для настройки WireGuard на Вашем устройстве:
1.Скачайте WireGuard из 
    App Store(iOS,iPadOS) — <a href='https://itunes.apple.com/us/app/wireguard/id1441195209?ls=1&mt=8'>ссылка</a>
    Google Play(Android) — <a href='https://play.google.com/store/apps/details?id=com.wireguard.android'>ссылка</a>
или
    с официального сайта —  <a href='https://www.wireguard.com/install/'>ссылка</a>
2.Скачайте конфиг-файл (имя вида "*.conf") ниже в чате
3.Откройте приложение WireGuard и нажмите на кнопку ➕
4.Выберите "Импорт" и найдите скачанный конфиг-файл в папке в который был скачан файл

В случае iOS,iPadOS:
2.Нажмите на конфиг-файл (имя вида "*.conf") ниже в чате
3.Нажмите кнопку "Поделиться"
4.Из списка программ выберите WireGuard


Альтернативно, QR-код можно переслать на другое устройство и отсканировать в WireGuard, нажав ➕.


Обратите внимание: Один QR-код или конфиг-файл может быть использован только на одном устройстве!""",
    "outline": """Инструкция для настройки Outline на Вашем устройстве:
1.Скачайте Outline из 
    App Store(iOS,iPadOS) — <a href='https://itunes.apple.com/us/app/outline-app/id1356177741'>ссылка</a>
    Google Play(Android) — <a href='https://play.google.com/store/apps/details?id=org.outline.android.client'>ссылка</a>
или
    с официального сайта (Скачайте Outline client)  —  <a href='https://getoutline.org/get-started/'>ссылка</a>
2. Скопируйте ключ ниже в чате
3.Откройте приложение Outline и нажмите на кнопку ➕
4.Вставьте ключ в поле и нажмите «Добавить сервер»

Обратите внимание: Один ключ может быть использован на разных устройствах!"""
}

menu_text = """Устройства и Тарифы:
    
WireGuard (WG):
1 конфиг: 100 руб/30 дней (3,33 руб/день, ежедневное списание).
⚠ Баланс распределяется между всеми конфигами.
Списание средств за конфиг будет произведено после предоставления 24-часового доступа.
Для получения настроек нажмите на имя устройства.

Outline (OL):
50 ГБ: 150 руб
100 ГБ: 249 руб
500 ГБ: 999 руб
1000 ГБ: 1500 руб

⚠ Списание разовое. Осуществляется сразу.
Дополнительные ГБ можно докупить на этот же ключ.
Чтобы получить ключ и узнать остаток трафика, нажмите на имя устройства."""


@dp.message_handler(commands="devices", state="*")
async def msg_device_menu(message: Message, state: FSMContext):
    await state.finish()
    devices = await db.get_devices_by_user_id(message.from_user.id)
    await message.answer(menu_text,
                         reply_markup=user_kb.get_devices(devices))


@dp.callback_query_handler(text="devices")
async def devices_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    devices = await db.get_devices_by_user_id(call.from_user.id)
    await call.message.answer(menu_text,
                              reply_markup=user_kb.get_devices(devices))
    await call.answer()


@dp.callback_query_handler(text="new_device")
async def new_device_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("""При выборе между WireGuard и Outline, учтите следующее:
  WireGuard: Не имеет ограничений по трафику. Однако он может быть заблокирован в некоторых регионах и один конфиг-файл может быть использован только на одном устройстве.
  Outline: Обеспечивает доступность во всех регионах, один ключ может быть использован на разных устройствах, но имеет ограничение по трафику.

Рекомендуем использовать WireGuard, если он доступен в вашем регионе. В противном случае, можно использовать Outline, чтобы обеспечить доступность везде, хотя с ограничением по трафику.   """,
                              reply_markup=user_kb.choose_device_type)
    await state.set_state(NewDevice.device_type)
    await call.answer()


@dp.callback_query_handler(state=NewDevice.device_type)
async def new_device_device_type(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    await state.update_data(device_type=call.data)
    if call.data == "outline":
        await call.message.edit_text("Выберите трафик:", reply_markup=user_kb.limit)
        return await state.set_state(NewDevice.limit)

    await state.update_data(device_type=call.data)
    await state.set_state(NewDevice.name)
    await call.message.edit_text("""Пример названия устройства:
«Мой телефон» или «Мой MacBook»

Введите название устройства:""", reply_markup=user_kb.inline_cancel)


@dp.callback_query_handler(user_kb.limit_data.filter(), state=NewDevice.limit)
async def new_device_limit(call: CallbackQuery, state: FSMContext, callback_data: dict):
    limit = int(callback_data["value"])
    user = await db.get_user(call.from_user.id)
    if user["balance"] < outline_prices[limit]:
        await call.message.edit_text("Недостаточно баланса для создания ключа", reply_markup=user_kb.show_menu)
        return await state.finish()
    await state.update_data(limit=limit)
    await state.set_state(NewDevice.name)
    await call.message.edit_text("""Пример названия устройства:
«Мой телефон» или «Мой MacBook»

Введите название устройства:""", reply_markup=user_kb.inline_cancel)


@dp.message_handler(state=NewDevice.name)
async def new_device_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(NewDevice.country)
    countries = await db.get_countries_for_new_device()
    await message.answer("""Выбор определенной страны в VPN означает, что ваша виртуальная локация совпадает с физическим местоположением в этой стране. Если вам это несущественно, то вы можете выбрать любую страну на свое усмотрение.

Выберите страну:""", reply_markup=user_kb.get_countries(countries))


@dp.callback_query_handler(user_kb.new_device_country.filter(), state=NewDevice.country)
async def new_device_country(call: CallbackQuery, state: FSMContext, callback_data: dict):
    data = await state.get_data()
    country_id = int(callback_data["country_id"])
    server = await db.get_current_server_by_country_id(country_id)
    device_id = await db.add_new_device(call.from_user.id, data["device_type"], data["name"], server["server_id"])
    await call.message.edit_text("Девайс успешно создан", reply_markup=user_kb.show_menu)
    price = 0
    await call.message.answer(instructions[data["device_type"]], disable_web_page_preview=True)
    if data["device_type"] == "wireguard":
        await server_utils.create_wireguard_config(server["ip_address"], server["server_password"], device_id)
        await server_utils.get_wireguard_config(server["ip_address"], server["server_password"], device_id,
                                                call.from_user.id)
        await call.message.answer_photo(open(f"OberVPN_{call.from_user.id}_{device_id}.png", "rb"))
        await call.message.answer_document(open(f"OberVPN_{call.from_user.id}_{device_id}.conf", "rb"),
                                           reply_markup=user_kb.show_menu)
        os.remove(f"OberVPN_{call.from_user.id}_{device_id}.png")
        os.remove(f"OberVPN_{call.from_user.id}_{device_id}.conf")
        price = 0
    elif data["device_type"] == "outline":
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.create_client(call.from_user.id, data["limit"])
        await call.message.answer(outline_client["accessUrl"],
                                  reply_markup=user_kb.show_menu)
        await db.set_outline_id(device_id, outline_client["id"])
        price = outline_prices[data["limit"]]
        await db.add_history_record(call.from_user.id, price, "Создание конфига")
    await db.update_user_balance(call.from_user.id, -price)

    await state.finish()


@dp.callback_query_handler(user_kb.delete_device.filter())
async def delete_device(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    device = await db.get_device(device_id)
    if device["device_type"] == "outline":
        server = await db.get_server(device["server_id"])
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.get_client(device["outline_id"])
        outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
        usage_gb = outline_client_usage // (1000 ** 3)
        limit_gb = outline_client['dataLimit']['bytes'] // (1000 ** 3)
        remaining_gb = limit_gb - usage_gb
        if usage_gb < limit_gb:
            return await call.message.answer(
                f"""Невозможно удалить устройство, пока у Вас есть свободный остаток трафика. Остаток трафика {remaining_gb}ГБ""")
    await call.message.answer("Вы действительно хотите удалить устройство?",
                              reply_markup=user_kb.get_delete_device(device_id))
    await call.answer()


@dp.callback_query_handler(user_kb.delete_device_action.filter())
async def delete_device_action(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    action = callback_data["action"]

    if action == "approve":
        device = await db.get_device(device_id)
        server = await db.get_server(device["server_id"])
        await db.delete_device(device_id)
        await call.message.edit_text("Устройство удалено", reply_markup=user_kb.show_menu)
        if device["device_type"] == "wireguard":
            await server_utils.delete_wireguard_config(server["ip_address"], server["server_password"], device_id)
        elif device["device_type"] == "outline":
            outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
            outline_manager.delete_client(device["outline_id"])
        await check_wireguard_active(call.from_user.id, call.bot)
    elif action == "cancel":
        await call.message.edit_text("Вы отказались от удаления аккаунта устройства!", reply_markup=user_kb.show_menu)


@dp.callback_query_handler(user_kb.device.filter())
async def device_menu(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    device = await db.get_device(device_id)
    server = await db.get_server(device["server_id"])
    await call.message.answer(instructions[device["device_type"]], disable_web_page_preview=True)
    if device["device_type"] == "wireguard":
        await server_utils.get_wireguard_config(server["ip_address"], server["server_password"], device_id,
                                                call.from_user.id)
        await call.message.answer_photo(open(f"OberVPN_{call.from_user.id}_{device_id}.png", "rb"))
        await call.message.answer_document(open(f"OberVPN_{call.from_user.id}_{device_id}.conf", "rb"),
                                           reply_markup=user_kb.show_menu)
        os.remove(f"OberVPN_{call.from_user.id}_{device_id}.png")
        os.remove(f"OberVPN_{call.from_user.id}_{device_id}.conf")
    elif device["device_type"] == "outline":
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.get_client(device["outline_id"])
        if outline_client is None:
            outline_client = outline_manager.create_client(call.from_user.id, 50)
            await db.set_outline_id(device_id, outline_client["id"])
        outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
        usage_gb = outline_client_usage // (1000 ** 3)
        limit_gb = outline_client['dataLimit']['bytes'] // (1000 ** 3)
        await call.message.answer(f"""Использовано {usage_gb}/{limit_gb}ГБ
{outline_client['accessUrl']}""", reply_markup=user_kb.get_add_limit(device_id))

    await call.answer()


@dp.callback_query_handler(user_kb.add_limit.filter())
async def add_limit(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    value = int(callback_data["value"])
    await call.message.answer("Вы действительно хотите увеличить трафик?",
                              reply_markup=user_kb.get_accept_add_limit(device_id, value))
    await call.answer()


@dp.callback_query_handler(user_kb.accept_add_limit.filter())
async def accept_add_limit(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    value = int(callback_data["value"])
    user = await db.get_user(call.from_user.id)
    if value == 0:
        return await call.message.answer("Вы отказались от добавления трафика", reply_markup=user_kb.show_menu)
    if user["balance"] < outline_prices[value]:
        return await call.message.answer("Недостаточно средств на балансе", reply_markup=user_kb.show_menu)
    device = await db.get_device(device_id)
    server = await db.get_server(device["server_id"])
    outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
    outline_client = outline_manager.get_client(device["outline_id"])
    outline_manager.set_data_limit(device["outline_id"], outline_client['dataLimit']['bytes'] // (1000 ** 3) + value)
    await db.update_user_balance(call.from_user.id, -outline_prices[value])
    await db.add_history_record(call.from_user.id, -outline_prices[value], "Продление лимита")
    await call.message.answer("Лимит успешно увеличен!", reply_markup=user_kb.show_menu)
    await call.answer()
