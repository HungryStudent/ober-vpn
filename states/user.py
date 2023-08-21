from aiogram.dispatcher.filters.state import StatesGroup, State


class NewDevice(StatesGroup):
    device_type = State()
    name = State()
    country = State()