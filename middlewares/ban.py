from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import database as db


class BanMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        user = await db.get_user(message.from_user.id)
        if user and user["is_banned"]:
            await message.answer(
                'Ваш аккаунт заблокирован!'
            )
            raise CancelHandler

    async def on_process_callback_query(self, call: CallbackQuery, data: dict):
        user = await db.get_user(call.from_user.id)
        if user and user["is_banned"]:
            await call.answer(
                'Ваш аккаунт заблокирован!',
                show_alert=True
            )
            raise CancelHandler
