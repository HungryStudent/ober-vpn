from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

admin_country = CallbackData("admin_country", "country_id")
admin_server = CallbackData("admin_server", "server_id")
set_default_server = CallbackData("set_default_server", "server_id")
change_server = CallbackData("change_server", "server_id", "field")
create_server = CallbackData("create_server", "country_id")

mailing = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Да, начать рассылку", callback_data="start_mailing"),
    InlineKeyboardButton("Нет", callback_data="stop_mailing"))

cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Отмена"))

menu = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Сервера", callback_data="admin_countries"),
                                             InlineKeyboardButton("Рассылка", callback_data="mailing"),
                                             InlineKeyboardButton("Статистика", callback_data="statistics"))


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
    kb.add(InlineKeyboardButton("Назад", callback_data="admin_countries"))
    return kb


def get_server(server):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Сделать основным", callback_data=set_default_server.new(server["server_id"])))
    kb.add(InlineKeyboardButton("Изменить IP", callback_data=change_server.new(server["server_id"], "ip")))
    kb.add(InlineKeyboardButton("Изменить пароль",
                                callback_data=change_server.new(server["server_id"], "server_password")))
    kb.add(InlineKeyboardButton("Назад", callback_data=admin_country.new(server["country_id"])))
