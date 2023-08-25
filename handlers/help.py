from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards.user as user_kb
from config_parser import BOT_NAME, wireguard_price
from create_bot import dp


@dp.callback_query_handler(state="*", text="help")
async def help_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("В разработке")
