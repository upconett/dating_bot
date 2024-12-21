from typing import List

from logic import CardWriter

from models import Card, Media
from logic.exceptions import CardNotFound, CardAlreadyExists

from sqlalchemy.exc import IntegrityError


class DefaultCardWriter(CardWriter):

    async def create(self, card: Card):
        try:
            await self._insert_new_card(card)
        except CardAlreadyExists:
            await self.update(card)
        await self._insert_card_media(card)


    async def update(self, card: Card):
        dct = self._compose_card_dict(card)
        await self.db.update(
            table="cards",
            filter_by={"id": card.id },
            data=dct,
        )
        await self._delete_card_media(card)
        await self._insert_card_media(card)


    async def delete(self, card: Card):
        await self.db.delete(
            table="cards",
            filter_by={"id": card.id }
        )
        await self._delete_card_media(card)

    
    async def delete_media(self, media: List[Media]):
        for m in media:
            await self.db.delete(
                table="card_media",
                filter_by={"id": m.file_id}
            )

    
    async def _insert_new_card(self, card: Card) -> bool:
        try:
            await self.db.insert(
                table="cards",
                data=self._compose_card_dict(card)
            )
        except IntegrityError:
            raise CardAlreadyExists()

    async def _delete_card_media(self, card: Card):
        await self.db.delete(
            table="card_media",
            filter_by={"card_id": card.id}
        )
    
    async def _insert_card_media(self, card: Card) -> bool:
        for media in card.media:
            await self.db.insert(
                table="card_media",
                data=self._compose_media_dict(media, card.id)
            )


    def _compose_card_dict(self, card: Card) -> dict:
        return {
            "id": card.id,
            "user_id": card.user_id,
            "name": card.name,
            "age": card.age,
            "city": card.city,
            "sex": card.sex.value,
            "interests": int(card.interests),
            "description": card.description,
            "active": card.active,
        }


    def _compose_media_dict(self, media: Media, card_id: int) -> dict:
        return {
            "id": media.file_id,
            "card_id": card_id,
            "type": media.type
        }
