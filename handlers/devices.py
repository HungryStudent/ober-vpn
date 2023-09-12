import os
from datetime import date, timedelta, datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.user as user_kb
from config_parser import outline_prices, wireguard_price
from create_bot import dp
from states.user import NewDevice
from utils import server as server_utils
from utils.devices import check_wireguard_active, get_days_text

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
1 конфиг — 30 дней Цена 100 руб.
⚠️ Оплата продлевается автоматически по окончанию месяца.
<b>Чтобы получить QR код с конфигом, нажмите на имя устройства.</b>

Outline (OL) Тарифы:
Бронза    — 30 дней/150ГБ Цена 100 руб
Серебро — 30 дней/300ГБ Цена 170 руб
Золото    — 30 дней/500ГБ Цена 250 руб

⚠️ Оплата продлевается автоматически по окончанию месяца.
<b>Чтобы получить ключ и <u>узнать остаток трафика</u>, нажмите на имя устройства.</b>"""


@dp.message_handler(commands="devices", state="*")
async def msg_device_menu(message: Message, state: FSMContext):
    await state.finish()
    devices = await db.get_devices_by_user_id(message.from_user.id)
    await message.answer(menu_text,
                         reply_markup=await user_kb.get_devices(devices))


@dp.callback_query_handler(text="devices")
async def devices_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    devices = await db.get_devices_by_user_id(call.from_user.id)
    await call.message.answer(menu_text,
                              reply_markup=await user_kb.get_devices(devices))
    await call.answer()


@dp.callback_query_handler(text="new_device")
async def new_device_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("""При выборе между WireGuard и Outline, учтите следующее:
  <b>WireGuard</b>: Не имеет ограничений по трафику. Однако он может быть заблокирован в некоторых регионах при использовании мобильного интернета или WiFi. Один конфиг-файл может быть использован только на одном устройстве.
  <b>Outline</b>: Обеспечивает доступность во всех регионах, один ключ может быть использован на разных устройствах, но имеет ограничение по трафику.

Для обеспечения максимальной доступности <b>рекомендуем</b> использовать <b>Outline</b>, так как при использовании WireGuard возможны проблемы с блокировками.""",
                              reply_markup=user_kb.choose_device_type)
    await state.set_state(NewDevice.device_type)
    await call.answer()


@dp.callback_query_handler(state=NewDevice.device_type)
async def new_device_device_type(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    await state.update_data(device_type=call.data)
    if call.data == "outline":
        await call.message.edit_text("""Выберите тариф:
Бронза    — 30 дней/150ГБ Цена 100 руб
Серебро — 30 дней/300ГБ Цена 170 руб
Золото    — 30 дней/500ГБ Цена 250 руб""",
                                     reply_markup=user_kb.get_limit())
        return await state.set_state(NewDevice.limit)
    elif user["balance"] <= wireguard_price:
        await call.message.edit_text("Недостаточно баланса для создания конфига", reply_markup=user_kb.show_menu)
        return await state.finish()
    await state.update_data(device_type=call.data)
    await state.set_state(NewDevice.name)
    await call.message.edit_text("""Пример названия устройства:
«Мой телефон» или «Мой MacBook»

Введите название устройства:""", reply_markup=user_kb.inline_cancel)


@dp.callback_query_handler(user_kb.limit_data.filter(), state=NewDevice.limit)
async def new_device_limit(call: CallbackQuery, state: FSMContext, callback_data: dict):
    product_id = callback_data["value"]
    user = await db.get_user(call.from_user.id)
    if user["balance"] < outline_prices[product_id]["price"]:
        await call.message.edit_text("Недостаточно баланса для создания ключа", reply_markup=user_kb.show_menu)
        return await state.finish()
    await state.update_data(product_id=product_id)
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
    product_id = data["product_id"] if "product_id" in data else None
    device_limit = None
    if product_id is not None:
        device_limit = outline_prices[product_id]["limit"]
    country_id = int(callback_data["country_id"])
    server = await db.get_current_server_by_country_id(country_id)
    sub_time = datetime.now() + timedelta(days=31)
    device_id = await db.add_new_device(call.from_user.id, data["device_type"], data["name"], server["server_id"],
                                        sub_time, product_id, device_limit)
    await call.message.edit_text("Девайс успешно создан", reply_markup=user_kb.show_menu)
    price = 0
    history_msg = "Создание конфига"
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
        price = wireguard_price
        history_msg = "Создание конфига"
    elif data["device_type"] == "outline":
        product = outline_prices[data["product_id"]]
        limit = product["limit"]
        price = product["price"]
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.create_client(call.from_user.id, limit)
        await call.message.answer(f"""Нажмите на ключ ниже, чтобы скопировать его 👇
<code>{outline_client['accessUrl']}</code>""",
                                  reply_markup=user_kb.show_menu)
        await db.set_outline_id(device_id, outline_client["id"])
        history_msg = "Создание ключа"

    await db.add_history_record(call.from_user.id, price, history_msg)
    await db.update_user_balance(call.from_user.id, -price)

    await state.finish()


@dp.callback_query_handler(text="delete_device")
async def delete_device_start(call: CallbackQuery, state: FSMContext):
    devices = await db.get_devices_by_user_id(call.from_user.id)
    await call.message.answer("Выберите устройство, которое вы хотите удалить:",
                              reply_markup=await user_kb.get_delete_devices(devices))
    await call.answer()


@dp.callback_query_handler(user_kb.delete_device.filter())
async def delete_device(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    device = await db.get_device(device_id)
    days = (device["sub_time"] - datetime.today()).days
    day_text = get_days_text(days)

    if device["device_type"] == "outline":
        server = await db.get_server(device["server_id"])
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.get_client(device["outline_id"])
        outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
        usage_gb = outline_client_usage // (1000 ** 3)
        limit_gb = outline_client['dataLimit']['bytes'] // (1000 ** 3)
        remaining_gb = limit_gb - usage_gb
        msg = f"""Не рекомендуем удалять устройство, поскольку Вам еще доступно {days} {day_text} и {remaining_gb} ГБ

Восстановление ключа будет невозможным."""
    else:
        msg = f"""Не рекомендуем удалять устройство, поскольку Вам еще доступно {days} {day_text}.

Восстановление конфиг-файла будет невозможным."""
    await call.message.answer(msg,
                              reply_markup=user_kb.get_delete_device(device_id))
    await call.answer()


@dp.callback_query_handler(user_kb.delete_device_action.filter())
async def delete_device_action(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    action = callback_data["action"]
    if action == "approve":
        await call.message.edit_text("Вы уверены, что хотите удалить устройство?",
                                     reply_markup=user_kb.get_accept_delete_device(device_id))
    elif action == "cancel":
        await call.message.edit_text("Вы отказались от удаления аккаунта устройства!", reply_markup=user_kb.show_menu)


@dp.callback_query_handler(user_kb.delete_device_approve.filter())
async def delete_device_approve(call: CallbackQuery, state: FSMContext, callback_data: dict):
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
        # await check_wireguard_active(call.from_user.id, call.bot)
    elif action == "cancel":
        await call.message.edit_text("Вы отказались от удаления аккаунта устройства!", reply_markup=user_kb.show_menu)


@dp.callback_query_handler(user_kb.device.filter())
async def device_menu(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    device = await db.get_device(device_id)
    server = await db.get_server(device["server_id"])
    await call.message.answer(instructions[device["device_type"]], disable_web_page_preview=True)
    if device["has_auto_renewal"]:
        auto_renewal_text = "Автопродление включено"
    else:
        auto_renewal_text = "Автопродление отключено"
    if device["device_type"] == "wireguard":
        await server_utils.get_wireguard_config(server["ip_address"], server["server_password"], device_id,
                                                call.from_user.id)
        await call.message.answer_photo(open(f"OberVPN_{call.from_user.id}_{device_id}.png", "rb"))
        days = (device["sub_time"] - datetime.today()).days
        active = ""
        is_active = True
        if days <= 0:
            is_active = False
            active = "\nКонфиг неактивен\n\n"
        if days < 0:
            days = 0
        day_text = get_days_text(days)

        await call.message.answer_document(open(f"OberVPN_{call.from_user.id}_{device_id}.conf", "rb"),
                                           caption=f"Осталось {days} {day_text}\n\n{active}{auto_renewal_text}",
                                           reply_markup=user_kb.get_wg_device(device, is_active))
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
        days = (device["sub_time"] - datetime.today()).days

        active = ""
        is_active = True
        if days <= 0 or usage_gb >= limit_gb:
            is_active = False
            active = "\nКлюч неактивен\n"
        if days < 0:
            days = 0
        day_text = get_days_text(days)
        await call.message.answer(f"""Осталось {days} {day_text}. Использовано {usage_gb}/{limit_gb}ГБ
{active}
{auto_renewal_text}

Нажмите на ключ ниже, чтобы скопировать его 👇
<code>{outline_client['accessUrl']}</code>""", reply_markup=user_kb.get_outline_device(device, is_active))

    await call.answer()


@dp.callback_query_handler(user_kb.auto_renewal.filter())
async def auto_renewal(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    device_id = int(callback_data["device_id"])
    status = True if callback_data["status"] == "True" else False
    await db.set_has_auto_renewal(device_id, status)
    device = await db.get_device(device_id)
    server = await db.get_server(device["server_id"])
    if device["has_auto_renewal"]:
        auto_renewal_text = "Автопродление включено"
    else:
        auto_renewal_text = "Автопродление отключено"
    if device["device_type"] == "wireguard":
        await server_utils.get_wireguard_config(server["ip_address"], server["server_password"], device_id,
                                                call.from_user.id)
        days = (device["sub_time"] - datetime.today()).days
        active = ""
        is_active = True
        if days <= 0:
            is_active = False
            active = "\nКонфиг неактивен\n\n"

        await call.message.edit_caption(
            caption=f"{active}{auto_renewal_text}",
            reply_markup=user_kb.get_wg_device(device, is_active))
        os.remove(f"OberVPN_{call.from_user.id}_{device_id}.png")
        os.remove(f"OberVPN_{call.from_user.id}_{device_id}.conf")
    else:
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.get_client(device["outline_id"])
        outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
        usage_gb = outline_client_usage // (1000 ** 3)
        limit_gb = outline_client['dataLimit']['bytes'] // (1000 ** 3)
        days = (device["sub_time"] - datetime.today()).days

        active = ""
        is_active = True
        if days <= 0 or usage_gb >= limit_gb:
            active = "\nКлюч неактивен\n"
            is_active = False
        day_text = get_days_text(days)
        await call.message.edit_text(f"""Осталось {days} {day_text}. Использовано {usage_gb}/{limit_gb}ГБ
{active}
{auto_renewal_text}

Нажмите на ключ ниже, чтобы скопировать его 👇
<code>{outline_client['accessUrl']}</code>""", reply_markup=user_kb.get_outline_device(device, is_active))


@dp.callback_query_handler(user_kb.resume_device.filter())
async def resume_device(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    device = await db.get_device(device_id)
    product = outline_prices[device["product_id"]]

    await call.message.answer(f"Тариф {product['name']} Цена {product['price']} руб. Подтвердить?",
                              reply_markup=user_kb.get_accept_resume_device(device_id))
    await call.answer()


@dp.callback_query_handler(user_kb.accept_resume_device.filter())
async def accept_resume_device(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    action = callback_data["action"]
    if action == "cancel":
        await call.message.edit_text("Вы отказались от возобновления тарифа", reply_markup=user_kb.show_menu)
        return
    device = await db.get_device(device_id)
    product = outline_prices[device["product_id"]]
    user = await db.get_user(call.from_user.id)
    if user["balance"] < product["price"]:
        return await call.message.edit_text("Недостаточно средств", reply_markup=user_kb.show_menu)
    sub_time = datetime.now() + timedelta(days=31)
    limit = device["outline_limit"] + product["limit"]
    await db.set_sub_time(device_id, sub_time)
    await db.set_outline_limit(device_id, limit)
    server = await db.get_server(device["server_id"])
    outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
    outline_manager.set_data_limit(device["outline_id"], limit)
    await db.update_user_balance(call.from_user.id, -product["price"])
    await call.message.edit_text("Тариф возобновлён", reply_markup=user_kb.show_menu)


@dp.callback_query_handler(user_kb.extend_device.filter())
async def extend_device(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    await call.message.answer(f"Подтвердить?",
                              reply_markup=user_kb.get_accept_extend_device(device_id))
    await call.answer()


@dp.callback_query_handler(user_kb.accept_extend_device.filter())
async def accept_extend_device(call: CallbackQuery, state: FSMContext, callback_data: dict):
    device_id = int(callback_data["device_id"])
    action = callback_data["action"]
    if action == "cancel":
        await call.message.edit_text("Вы отказались от продления тарифа", reply_markup=user_kb.show_menu)
        return
    user = await db.get_user(call.from_user.id)
    if user["balance"] < wireguard_price:
        return await call.message.edit_text("Недостаточно средств", reply_markup=user_kb.show_menu)
    sub_time = datetime.now() + timedelta(days=31)
    await db.set_sub_time(device_id, sub_time)
    await db.update_user_balance(call.from_user.id, -wireguard_price)
    await call.message.edit_text("Тариф возобновлён", reply_markup=user_kb.show_menu)

# @dp.callback_query_handler(user_kb.add_limit.filter())
# async def add_limit(call: CallbackQuery, state: FSMContext, callback_data: dict):
#     device_id = int(callback_data["device_id"])
#     value = int(callback_data["value"])
#     await call.message.answer("Вы действительно хотите увеличить трафик?",
#                               reply_markup=user_kb.get_accept_add_limit(device_id, value))
#     await call.answer()
#
#
# @dp.callback_query_handler(user_kb.accept_add_limit.filter())
# async def accept_add_limit(call: CallbackQuery, state: FSMContext, callback_data: dict):
#     device_id = int(callback_data["device_id"])
#     value = int(callback_data["value"])
#     user = await db.get_user(call.from_user.id)
#     if value == 0:
#         return await call.message.answer("Вы отказались от добавления трафика", reply_markup=user_kb.show_menu)
#     if value != FREE_LIMIT and user["balance"] < outline_prices[value]:
#         return await call.message.answer("Недостаточно средств на балансе", reply_markup=user_kb.show_menu)
#     if value == FREE_LIMIT and not user["has_free_outline"]:
#         await call.answer()
#         return await call.message.answer("Произошла ошибка!")
#
#     device = await db.get_device(device_id)
#     server = await db.get_server(device["server_id"])
#     outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
#     outline_client = outline_manager.get_client(device["outline_id"])
#     outline_manager.set_data_limit(device["outline_id"], outline_client['dataLimit']['bytes'] // (1000 ** 3) + value)
#     if value == FREE_LIMIT:
#         await db.set_has_free_outline(call.from_user.id, False)
#     else:
#         await db.update_user_balance(call.from_user.id, -outline_prices[value])
#         await db.add_history_record(call.from_user.id, -outline_prices[value], "Продление лимита")
#     await call.message.answer("Лимит успешно увеличен!", reply_markup=user_kb.show_menu)
#     await call.answer()
