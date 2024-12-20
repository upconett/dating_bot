from aiogram.filters import BaseFilter
from aiogram.types import Message as AIOgramMessage
from telegram import Config

config = Config(".env")  # TODO : come up with a way to not use two different instances (see initialisations.py)

class IsAdmin(BaseFilter):
    async def __call__(self, message: AIOgramMessage):
        if message.from_user.id in config.admins:
            return True
        return False
