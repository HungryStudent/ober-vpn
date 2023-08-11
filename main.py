from aiogram.utils import executor
from create_bot import dp
import database as db
from handlers import user
from handlers import admin


async def on_startup(_):
    await db.create_models()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
