from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from config_parser import ADMINS
import database as db


class IsAdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.global_admin = is_admin

    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        admins = await db.get_users_with_admin()
        admins_list = [admin["user_id"] for admin in admins]
        if user.id in admins_list or user.id in ADMINS:
            return self.global_admin is True
        return self.global_admin is False


class IsSuperAdminFilter(BoundFilter):
    key = "is_super_admin"

    def __init__(self, is_super_admin: bool):
        self.global_admin = is_super_admin

    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        if user.id in ADMINS:
            return self.global_admin is True
        else:
            await obj.bot.send_message(user.id, "нет доступа!")
        return self.global_admin is False
