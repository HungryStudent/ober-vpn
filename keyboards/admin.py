from datetime import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from config_parser import outline_prices
import database as db
import utils.server as server_utils
from utils.devices import get_days_text

admin_country = CallbackData("admin_country", "country_id")
change_country = CallbackData("change_country", "country_id", "field")
hidden_country = CallbackData("hidden_country", "country_id", "status")
delete_country = CallbackData("delete_country", "country_id")
admin_server = CallbackData("admin_server", "server_id")
delete_server = CallbackData("delete_server", "server_id")
delete_server_action = CallbackData("delete_server_action", "server_id", "action")
set_default_server = CallbackData("set_default_server", "server_id")
change_server = CallbackData("change_server", "server_id", "field")
create_server = CallbackData("create_server", "country_id")
admin_device = CallbackData("admin_device", "device_id")
admin_add_limit = CallbackData("admin_add_limit", "device_id", "value")
ban_user = CallbackData("ban_user", "user_id", "action")
delete_user_action = CallbackData("delete_user", "user_id", "action")
change_admin = CallbackData("change_admin", "action")

mailing = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Да, начать рассылку", callback_data="start_mailing"),
    InlineKeyboardButton("Нет", callback_data="stop_mailing"))

cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Отмена"))

menu = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Сервера", callback_data="admin_countries"),
                                             InlineKeyboardButton("Рассылка", callback_data="mailing"),
                                             InlineKeyboardButton("Статистика", callback_data="statistics"),
                                             InlineKeyboardButton("Конфиги", callback_data="admin_devices"),
                                             InlineKeyboardButton("Бан/Разбан", callback_data="admin_ban"),
                                             InlineKeyboardButton("Изменить баланс", callback_data="admin_balance"),
                                             InlineKeyboardButton("Пополнения", callback_data="admin_pay_history"),
                                             InlineKeyboardButton("Удалить пользователя", callback_data="delete_user"),
                                             InlineKeyboardButton("Ежедневный отчет", callback_data="report"),
                                             InlineKeyboardButton("Админы", callback_data="admins"))

admins_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Добавить админа", callback_data=change_admin.new("add")),
    InlineKeyboardButton("Удалить админа", callback_data=change_admin.new("delete")))


def get_countries(countries):
    kb = InlineKeyboardMarkup(row_width=1)
    for country in countries:
        kb.add(InlineKeyboardButton(country["name"], callback_data=admin_country.new(country["country_id"])))
    kb.add(InlineKeyboardButton("Добавить страну", callback_data="create_country"))
    kb.add(InlineKeyboardButton("Назад", callback_data="admin_menu"))
    return kb


def get_country(country, servers):
    kb = InlineKeyboardMarkup(row_width=1)
    for server in servers:
        kb.add(InlineKeyboardButton(server["ip_address"], callback_data=admin_server.new(server["server_id"])))
    kb.add(InlineKeyboardButton("Добавить сервер", callback_data=create_server.new(country["country_id"])))
    kb.add(InlineKeyboardButton("Изменить название", callback_data=change_country.new(country["country_id"], "name")))
    if country["is_hidden"]:
        is_hidden_text = "Показать страну"
    else:
        is_hidden_text = "Скрыть страну"
    kb.add(InlineKeyboardButton(is_hidden_text,
                                callback_data=hidden_country.new(country["country_id"], not country["is_hidden"])))
    kb.add(InlineKeyboardButton("Удалить страну", callback_data=delete_country.new(country["country_id"])))
    kb.add(InlineKeyboardButton("Назад", callback_data="admin_countries"))
    return kb


def get_server(server):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Сделать основным", callback_data=set_default_server.new(server["server_id"])))
    kb.add(InlineKeyboardButton("Изменить пароль",
                                callback_data=change_server.new(server["server_id"], "password")))
    kb.add(InlineKeyboardButton("Удалить сервер", callback_data=delete_server.new(server["server_id"])))
    kb.add(InlineKeyboardButton("Назад", callback_data=admin_country.new(server["country_id"])))
    return kb


def get_delete_server(server_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("Да, удалить", callback_data=delete_server_action.new(server_id, "approve")),
           InlineKeyboardButton("Не удалять", callback_data=delete_server_action.new(server_id, "cancel")))
    return kb


async def get_devices(devices):
    kb = InlineKeyboardMarkup(row_width=2)
    for my_device in devices:
        device_type = "(WG)" if my_device["device_type"] == "wireguard" else "(OL)"
        days = (my_device["sub_time"] - datetime.today()).days
        day_text = get_days_text(days)
        limit = ""
        if my_device["device_type"] == "outline":
            server = await db.get_server(my_device["server_id"])
            outline_manager = server_utils.Outline(server["outline_url"], server["outline_sha"])
            outline_client = outline_manager.get_client(my_device["outline_id"])
            try:
                outline_client_usage = outline_manager.get_usage_data(outline_client["id"])
            except TypeError:
                outline_client_usage = 0
            usage_gb = outline_client_usage // (1000 ** 3)
            limit = f"({usage_gb}/{my_device['outline_limit']}ГБ)"
        kb.add(InlineKeyboardButton(f"{device_type}({days} {day_text}){limit} {my_device['name']}",
                                    callback_data=admin_device.new(my_device["device_id"])))
    return kb


def get_add_limit(device_id):
    kb = InlineKeyboardMarkup(row_width=1)
    for price in outline_prices:
        kb.add(InlineKeyboardButton(f"Добавить {price}ГБ", callback_data=admin_add_limit.new(device_id, price)))
    return kb


def get_ban(user_id, action):
    kb = InlineKeyboardMarkup(row_width=1)
    ban_text = {"ban": "Заблокировать", "unban": "Разблокировать"}
    kb.add(InlineKeyboardButton(ban_text[action], callback_data=ban_user.new(user_id, action)))
    return kb


def get_delete_user(user_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("Да, удалить", callback_data=delete_user_action.new(user_id, "approve")),
           InlineKeyboardButton("Не удалять", callback_data=delete_user_action.new(user_id, "cancel")))
    return kb
