from typing import *

from models import Statistics

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