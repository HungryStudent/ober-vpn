from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound

from config_parser import ADMINS
from create_bot import dp, bot
import database as db
import handlers


async def on_startup(_):
    await db.create_models()
    commands = [BotCommand(command='/start', description="🏠Главное меню"),
                BotCommand(command='/devices', description="📱Мои устройства"),
                BotCommand(command='/topup', description="💵Пополнить баланс"),
                BotCommand(command='/invite', description="👨‍⚕Пригласить друга")]
    await bot.set_my_commands(commands)
    commands.append(BotCommand(command='/admin', description="Админка"))
    for admin_id in ADMINS:
        try:
            await bot.set_my_commands(commands,
                                      scope=BotCommandScopeChat(admin_id))
        except ChatNotFound:
            continue


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
