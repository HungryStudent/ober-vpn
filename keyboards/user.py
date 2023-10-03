from datetime import date, datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from config_parser import outline_prices
from utils import server as server_utils
import database as db
from utils.devices import get_days_text

device = CallbackData("device", "device_id")
delete_device = CallbackData("delete_device", "device_id")
delete_device_action = CallbackData("delete_device_action", "device_id", "action")
delete_device_approve = CallbackData("delete_device_approve", "device_id", "action")
new_device_country = CallbackData("new_device_country", "country_id")
payment = CallbackData("payment", "amount")
add_limit = CallbackData("add_limit", "device_id", "value")
accept_add_limit = CallbackData("accept_add_limit", "device_id", "value")
limit_data = CallbackData("limit", "value")
help_post = CallbackData("help_post", "post")
auto_renewal = CallbackData("auto_renewal", "device_id", "status")
resume_device = CallbackData("resume_device", "device_id")
accept_resume_device = CallbackData("accept_resume_device", "device_id", "action")
extend_device = CallbackData("extend", "device_id")
accept_extend_device = CallbackData("extend", "device_id", "action")
tg_pay = CallbackData("tg_pay", "amount")

inline_cancel = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Отмена", callback_data="cancel"))

start = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🎉 ПОДКЛЮЧИТЬ VPN 🎉", callback_data="show_menu"))

show_menu = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🏠Главное меню", callback_data="show_menu"))

menu = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("📱Мои устройства", callback_data="devices")
).add(
    InlineKeyboardButton("📹 Видеоинструкции", callback_data="video_help")
).add(
    InlineKeyboardButton("💵Пополнить", callback_data="balance_menu"),
    InlineKeyboardButton("🧍‍♂️Пригласить", callback_data="ref_menu")

).add(InlineKeyboardButton("🧾Платежи", callback_data="history"),
      InlineKeyboardButton("📖Помощь", callback_data="help"))

choose_device_type = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("WireGuard", callback_data="wireguard"),
    InlineKeyboardButton("Outline", callback_data="outline")
)

balance_amounts = [100, 200, 300, 500, 1000, 2000]
balance = InlineKeyboardMarkup(row_width=3).add(
    *[InlineKeyboardButton(text=f"{amount}₽", callback_data=payment.new(amount)) for amount in balance_amounts])
balance.add(InlineKeyboardButton("Указать свою сумму", callback_data=payment.new(0)))

support = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Не работает VPN", callback_data=help_post.new("no_work")),
    InlineKeyboardButton("Низкая скорость", callback_data=help_post.new("small_speed")),
    InlineKeyboardButton("Другое", callback_data=help_post.new("other")))

first_device = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Другое", callback_data="first_device"))

help_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🛠️Техподдержка", url="https://t.me/obervpn_chat"),
    InlineKeyboardButton("🏠Главное меню", callback_data="show_menu")
)


async def params_for_device(my_device):
    device_type = "(WG)" if my_device["device_type"] == "wireguard" else "(OL)"
    days = (my_device["sub_time"] - datetime.today()).days
    if my_device["sub_time"].date() == datetime.today().date():
        days = 1
    if days == 0:
        days = 1
    if days < 0:
        days = 0
    day_text = get_days_text(days)
    limit = ""
    if my_device["device_type"] == "outline":
        server = await db.get_server(my_device["server_id"])
        outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
        outline_client = outline_manager.get_client(my_device["outline_id"])
        outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
        print(my_device["outline_traffic"])
        usage_gb = outline_client_usage // (1000 ** 3) - my_device["outline_traffic"]
        limit = f"({usage_gb}/{my_device['outline_limit']})"
    return {"device_type": device_type, "days": days, "limit": limit, "day_text": day_text}


async def get_devices(devices):
    kb = InlineKeyboardMarkup(row_width=2)
    for my_device in devices:
        print("1")
        params = await params_for_device(my_device)
        kb.add(InlineKeyboardButton(
            f"{params['device_type']}({params['days']} {params['day_text']}){params['limit']} {my_device['name']}",
            callback_data=device.new(my_device["device_id"])))
    kb.add(InlineKeyboardButton("❌ Удаление устройств", callback_data="delete_device"))
    kb.add(InlineKeyboardButton("➕ Добавить устройство", callback_data="new_device"))
    kb.add(InlineKeyboardButton("🏠Главное меню", callback_data="show_menu"))
    return kb


def get_countries(countries):
    kb = InlineKeyboardMarkup(row_width=1)
    for country in countries:
        kb.add(InlineKeyboardButton(country["name"], callback_data=new_device_country.new(country["country_id"])))
    return kb


async def get_delete_devices(devices):
    kb = InlineKeyboardMarkup(row_width=2)
    for my_device in devices:
        params = await params_for_device(my_device)

        kb.add(InlineKeyboardButton(
            f"{params['device_type']}({params['days']} {params['day_text']}){params['limit']} {my_device['name']}",
            callback_data=delete_device.new(my_device["device_id"])))
    kb.add(InlineKeyboardButton("Назад", callback_data="devices"))
    kb.add(InlineKeyboardButton("🏠Главное меню", callback_data="show_menu"))
    return kb


def get_delete_device(device_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("❌ Всё равно удалить", callback_data=delete_device_action.new(device_id, "approve")))
    kb.add(InlineKeyboardButton("Назад", callback_data="devices"))
    kb.add(InlineKeyboardButton("🏠Главное меню", callback_data="show_menu"))
    return kb


def get_accept_delete_device(device_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("Да", callback_data=delete_device_approve.new(device_id, "approve")),
           InlineKeyboardButton("Нет", callback_data=delete_device_approve.new(device_id, "cancel")))
    return kb


def get_limit():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        *[InlineKeyboardButton(product['name'],
                               callback_data=limit_data.new(product_id))
          for (product_id, product) in outline_prices.items()]
    )
    return kb


#
# def get_add_limit(device_id):
#     kb = InlineKeyboardMarkup(row_width=1)
#     for (amount, price) in outline_prices.items():
#         kb.add(InlineKeyboardButton(f"{amount} ГБ: {price} руб", callback_data=add_limit.new(device_id, amount)))
#     kb.add(InlineKeyboardButton("🏠Главное меню", callback_data="show_menu"))
#     return kb

def get_outline_device(device, is_active):
    kb = InlineKeyboardMarkup(row_width=1)
    if not is_active:
        kb.add(InlineKeyboardButton("Возобновить тариф", callback_data=resume_device.new(device["device_id"])))

    if device["has_auto_renewal"]:
        auto_renewal_text = "Откл. Автопродление"
    else:
        auto_renewal_text = "Вкл. Автопродление"
    kb.add(InlineKeyboardButton(auto_renewal_text,
                                callback_data=auto_renewal.new(device["device_id"],
                                                               not device["has_auto_renewal"])))
    kb.add(InlineKeyboardButton("Назад", callback_data="devices"))
    kb.add(InlineKeyboardButton("🏠Главное меню", callback_data="show_menu"))
    return kb


def get_wg_device(device, is_active):
    kb = InlineKeyboardMarkup(row_width=1)
    if not is_active:
        kb.add(InlineKeyboardButton("Продлить", callback_data=extend_device.new(device["device_id"])))

    if device["has_auto_renewal"]:
        auto_renewal_text = "Откл. Автопродление"
    else:
        auto_renewal_text = "Вкл. Автопродление"
    kb.add(InlineKeyboardButton(auto_renewal_text,
                                callback_data=auto_renewal.new(device["device_id"],
                                                               not device["has_auto_renewal"])))
    kb.add(InlineKeyboardButton("Назад", callback_data="devices"))
    kb.add(InlineKeyboardButton("🏠Главное меню", callback_data="show_menu"))
    return kb


def get_accept_extend_device(device_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Да", callback_data=accept_extend_device.new(device_id, "approve")),
           InlineKeyboardButton("Нет", callback_data=accept_extend_device.new(device_id, "cancel")))
    return kb


def get_accept_resume_device(device_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Да", callback_data=accept_resume_device.new(device_id, "approve")),
           InlineKeyboardButton("Нет", callback_data=accept_resume_device.new(device_id, "cancel")))
    return kb


def get_accept_add_limit(device_id, amount):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Да", callback_data=accept_add_limit.new(device_id, amount)),
           InlineKeyboardButton("Нет", callback_data=accept_add_limit.new(device_id, 0)))
    return kb


def get_payment_url(url, amount):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("СПБ", url=url))
    kb.add(InlineKeyboardButton("Картой", callback_data=tg_pay.new(amount)))
    return kb
