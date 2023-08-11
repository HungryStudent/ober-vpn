from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from config_parser import ADMINS


class IsAdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.global_admin = is_admin

    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        if user.id in ADMINS:
            return self.global_admin is True
        return self.global_admin is False
