from aiogram.filters import BaseFilter
from aiogram import types

from settings import WHITE_LIST, DATABASE_NAME
from db.db_manage import DataBase
from bot.utils import sort_data_by_market


class IsAdmin(BaseFilter):
    def __init__(self):
        self.white_list = WHITE_LIST

    async def __call__(self, message: types.Message):
        return message.from_user.id in self.white_list
