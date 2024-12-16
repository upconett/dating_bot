from typing import List

from logic import CardWriter, CardLoader

from models import Card, User, Media

from logic.exceptions import CardNotFound

class CardService:
    card_writer: CardWriter
    card_loader: CardLoader


    def __init__(
            self,
            card_writer: CardWriter, 
            card_loader: CardLoader
        ):
        self.card_writer = card_writer
        self.card_loader = card_loader


    async def create(self, card: Card, user: User) -> Card:
        card.id = user.id
        card.user_id = user.tg_id
        await self.card_writer.create(card)
        return card

    async def get_by_user(self, user: User) -> Card:
        return await self.card_loader.get_by_id(user.id)

    async def get_recomended(self, user: User) -> Card:
        return await self.card_loader.get_recomended(user)

    async def update_recomendations(self, user: User):
        await self.card_loader.make_all_cards_as_unseen(user)

    async def update_card(self, card: Card):
        await self.card_writer.update(card)

    async def user_has_card(self, user: User) -> bool:
        try:
            await self.card_loader.get_by_id(user.id)
            return True
        except CardNotFound:
            return False
