from aiogram.dispatcher.filters.state import StatesGroup, State


class Mailing(StatesGroup):
    text = State()


class CreateCountry(StatesGroup):
    name = State()


class CreateServer(StatesGroup):
    ip_address = State()
    server_password = State()


class ChangeServer(StatesGroup):
    new_value = State()


class ChangeCountry(StatesGroup):
    new_value = State()


class FindDevices(StatesGroup):
    user_id = State()


class BanUser(StatesGroup):
    user_id = State()


class ChangeBalanceUser(StatesGroup):
    user_id = State()
    amount = State()