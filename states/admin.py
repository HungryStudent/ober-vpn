from aiogram.dispatcher.filters.state import StatesGroup, State


class Mailing(StatesGroup):
    text = State()


class CreateCountry(StatesGroup):
    name = State()