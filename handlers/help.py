from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

import keyboards.user as user_kb
from create_bot import dp

help_texts = {
    "no_work": """❗️ Внимание! Из-за блокировок в России, WireGuard нестабилен, особенно при мобильном интернете. 

Если не работает VPN, необходимо:

👉 Проверить наличие оставшихся дней доступности устройства.
👉 Проверить наличие оставшегося трафика устройства, если используется  Outline VPN.
👉 Обновить приложение, если необходимо 
👉 Перезагрузить телефон  """,
    "small_speed": "Мы стремимся поддерживать оптимальную загрузку наших серверов, и низкая скорость обычно связана с проблемой местных или транзитных провайдеров. Нагрузки растут, а новые каналы связи в Европу в условиях санкций не строятся. Нагрузка также зависит от времени суток.",
    "other": "Если вы не обнаружили подходящую для вас тему, не стесняйтесь обратиться к нам в техподдержку."
}


@dp.callback_query_handler(state="*", text="help")
async def help_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Выберите тему для получения помощи", reply_markup=user_kb.support)
    await call.answer()


@dp.callback_query_handler(user_kb.help_post.filter())
async def help_post(call: CallbackQuery, state: FSMContext, callback_data: dict):
    post = callback_data["post"]
    await call.message.answer(help_texts[post], reply_markup=user_kb.help_menu)
    await call.answer()


@dp.callback_query_handler(text="video_help")
async def video_help(call: CallbackQuery, state: FSMContext):
    await call.message.answer("""Ниже представлены ссылки на видеоинструкции по настройке VPN:

iOS/iPadOS:
Настройка Outline —  <a href='https://youtu.be/TzBHYfvZ4jE'>ссылка</a>
Настройка WireGuard — <a href='https://youtu.be/56ULmBV4QSE'>ссылка</a>

Android:
Настройка Outline —  <a href='https://youtu.be/PIvgt_43RRo'>ссылка</a>
Настройка WireGuard — <a href='https://youtu.be/doCCWT-dAEI'>ссылка</a>""", reply_markup=user_kb.show_menu,
                              disable_web_page_preview=True)
    await call.answer()
