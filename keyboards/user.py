from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

device = CallbackData("device", "device_id")
delete_device = CallbackData("delete_device", "device_id")
delete_device_action = CallbackData("delete_device_action", "device_id", "action")
new_device_country = CallbackData("new_device_country", "country_id")
payment = CallbackData("payment", "amount")
add_limit = CallbackData("add_limit", "device_id")

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

balance_amounts = [100, 200, 300, 400, 500, 700, 1000, 2000, 3000]
balance = InlineKeyboardMarkup(row_width=3).add(
    *[InlineKeyboardButton(text=f"{amount}₽", callback_data=payment.new(amount)) for amount in balance_amounts])


def get_devices(devices):
    kb = InlineKeyboardMarkup(row_width=2)
    for my_device in devices:
        kb.add(InlineKeyboardButton(my_device["name"], callback_data=device.new(my_device["device_id"])),
               InlineKeyboardButton("❌ Удалить", callback_data=delete_device.new(my_device["device_id"])))
    kb.add(InlineKeyboardButton("Добавить устройство", callback_data="new_device"))
    return kb


def get_countries(countries):
    kb = InlineKeyboardMarkup(row_width=1)
    for country in countries:
        kb.add(InlineKeyboardButton(country["name"], callback_data=new_device_country.new(country["country_id"])))
    return kb


def get_delete_device(device_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("Да, удалить", callback_data=delete_device_action.new(device_id, "approve")),
           InlineKeyboardButton("Не удалять", callback_data=delete_device_action.new(device_id, "cancel")))
    return kb


def get_add_limit(device_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Добавить 100ГБ", callback_data=add_limit.new(device_id)))
    return kb
