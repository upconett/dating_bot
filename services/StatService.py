from typing import *
import asyncio

from models import Statistics, User

from logic import (
    UserLoader, UserWriter,
    CardLoader
)

class StatService:
    user_loader: UserLoader
    user_writer: UserWriter
    card_loader: CardLoader

    def __init__(
            self,
            user_loader: UserLoader,
            user_writer: UserWriter,
            card_loader: CardLoader,
        ):
        self.user_loader = user_loader
        self.user_writer = user_writer
        self.card_loader = card_loader

    async def get_full_statistics(self) -> Statistics:
        cards_count = await self.card_loader.count_cards()
        male_count = await self.card_loader.count_male()
        stats = Statistics(
            users_count=await self.user_loader.count_users(),
            active_users_count=await self.user_loader.count_active_users(),
            cards_count=cards_count,
            male_count=male_count,
            female_count=cards_count-male_count,
            users_who_liked_count=await self.user_loader.count_with_at_least_1_like(),
            users_who_messaged_count=await self.user_loader.count_with_at_least_1_message(),
            total_likes_count=await self.user_loader.get_total_likes_count(),
            total_messages_count=await self.user_loader.get_total_messages_count(),
        )
        return stats

    async def can_like(self, user: User) -> bool:
        return user.bonus_likes > 0 or user.likes_left > 0

    async def can_message(self, user: User) -> bool:
        return user.bonus_messages > 0 or user.messages_left > 0

    async def add_liked(self, user: User) -> None:
        await self.user_writer.add_liked(user)

    async def add_messaged(self, user: User) -> None:
        await self.user_writer.add_messaged(user)

    async def add_bonus_likes(self, user: User) -> None:
        user.bonus_likes += 40
        await self.user_writer.update(user)

    async def add_bonus_messages(self, user: User) -> None:
        user.bonus_messages += 5
        await self.user_writer.update(user)

    async def stats_cycle(self) -> None:
        print("Starting stats cycle")
        while True:
            await asyncio.sleep(60) # TODO : set to 60 * 60 * 24
            print("cycle passed, reseting liked and messaged")
            await self.user_writer.reset_likes_and_messages()

    async def start_stats_cycle(self) -> None:
        self.task = asyncio.create_task(self.stats_cycle())
