from logic import UserLoader, UserWriter

from telegram import AIOgramChat
from models import User, Card

from logic.static import UserAdapter
from logic.exceptions import *


class UserService:
    user_loader: UserLoader
    user_writer: UserWriter


    def __init__(self, user_loader: UserLoader, user_writer: UserWriter):
        self.user_loader = user_loader
        self.user_writer = user_writer


    async def update_cached(self, user: User) -> User:
        await self.user_loader.remove_from_cache(user.tg_id, user.id)
        if user.tg_id:
            return await self.user_loader.get_by_tg_id(user.tg_id)
        else:
            return await self.user_loader.get_by_internal_id(user.id)
    
    async def get_by_card(self, card: Card) -> User:
        return await self.user_loader.get_by_internal_id(card.id)

    async def get_by_tg_id(self, tg_id: int) -> User:
        return await self.user_loader.get_by_tg_id(tg_id)

    async def get_by_id(self, internal_id: int) -> User:
        return await self.user_loader.get_by_internal_id(internal_id)

    async def get_by_chat(self, chat: AIOgramChat) -> User:
        try:
            return await self.user_loader.get_by_tg_id(chat.id)
        except UserNotFound:
            raw_user = UserAdapter.from_aiogram_chat(chat)
            await self.user_writer.create(raw_user)
            return await self.user_loader.get_by_tg_id(chat.id)


    async def update_user(self, user: User) -> None:
        try:
            await self.user_writer.update(user)
        except UserNotFound:
            await self.user_writer.create(user)
        except SettingsNotCreated:
            print("Blyat, cho za huyna")

    async def ban_user(self, user: User) -> None:
        user.banned = True
        await self.user_writer.update(user)

    async def unban_user(self, user: User) -> None:
        user.banned = False
        await self.user_writer.update(user)
