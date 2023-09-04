from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

import keyboards.user as user_kb
from create_bot import dp

help_texts = {"install": "ПОМОЩЬ 1"}


@dp.callback_query_handler(state="*", text="help")
async def help_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Выберите тему для получения помощи", reply_markup=user_kb.support)
    await call.answer()


@dp.callback_query_handler(user_kb.help_post.filter())
async def help_post(call: CallbackQuery, state: FSMContext, callback_data: dict):
    post = callback_data["post"]
    await call.message.answer(help_texts[post])
    await call.answer()


@dp.callback_query_handler(text="video_help")
async def video_help(call: CallbackQuery, state: FSMContext):
    await call.message.answer("https://www.youtube.com/watch?v=OU00dKQYUMI")
    await call.answer()