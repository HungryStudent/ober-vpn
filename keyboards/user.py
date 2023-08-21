from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

device = CallbackData("device", "device_id")
new_device_country = CallbackData("new_device_country", "country_id")

inline_cancel = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Отмена", callback_data="cancel"))

menu = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Пригласить", callback_data="ref_menu"),
    InlineKeyboardButton("Мои устройства", callback_data="devices"),
    InlineKeyboardButton("Помощь", callback_data="help"),
    InlineKeyboardButton("Пополнить баланс", callback_data="balance_menu")
)

choose_device_type = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("WireGuard", callback_data="wireguard"),
    InlineKeyboardButton("Outline", callback_data="outline")
)


def get_devices(devices):
    kb = InlineKeyboardMarkup(row_width=1)
    for my_device in devices:
        kb.add(InlineKeyboardButton(my_device["name"], callback_data=device.new(my_device["device_id"])))
    kb.add(InlineKeyboardButton("Добавить устройство", callback_data="new_device"))
    return kb


def get_countries(countries):
    kb = InlineKeyboardMarkup(row_width=1)
    for country in countries:
        kb.add(InlineKeyboardButton(country["name"], callback_data=new_device_country.new(country["country_id"])))
    return kb
