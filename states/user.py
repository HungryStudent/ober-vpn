from aiogram.dispatcher.filters.state import StatesGroup, State


class NewDevice(StatesGroup):
    device_type = State()
    os_type = State()
    limit = State()
    name = State()
    country = State()


class BalanceAmount(StatesGroup):
    amount = State()