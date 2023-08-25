from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound

from config_parser import ADMINS
from create_bot import dp, bot
import database as db
import handlers


async def on_startup(_):
    await db.create_models()
    await bot.set_my_commands([BotCommand(command='/start', description="Главное меню")])
    for admin_id in ADMINS:
        try:
            await bot.set_my_commands([BotCommand(command='/start', description="Главное меню"),
                                       BotCommand(command='/admin', description="Админка")],
                                      scope=BotCommandScopeChat(admin_id))
        except ChatNotFound:
            continue


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
