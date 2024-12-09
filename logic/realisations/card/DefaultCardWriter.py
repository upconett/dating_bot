from logic import CardWriter

from models import Card, Media
from logic.exceptions import CardNotFound


class DefaultCardWriter(CardWriter):

    async def create(self, card: Card):
        await self._insert_new_card(card)
        card.id = await self._get_generated_card_id(card)
        await self._insert_card_media(card)


    async def update(self, card: Card):
        await self.db.update(
            table="cards",
            filter_by={"id": card.id },
            data=self._compose_card_dict(card)
        )


    async def delete(self, card: Card):
        await self.db.delete(
            table="cards",
            filter_by={"id": card.id }
        )

    
    async def _insert_new_card(self, card: Card) -> bool:
        await self.db.insert(
            table="cards",
            data=self._compose_card_dict(card)
        )

    
    async def _insert_card_media(self, card: Card) -> bool:
        for media in card.media:
            await self.db.insert(
                table="media",
                data=self._compose_media_dict(media, card.id)
            )
        

    async def _get_generated_card_id(self, card: Card) -> int:
        result = await self.db.select(
            "cards",
            filter_by={"user_id": card.user_id}
        )
        if len(result) == 0:
            raise CardNotFound()
        card_db = result[0]
        return card_db.get("id")



    def _compose_card_dict(self, card: Card) -> dict:
        return {
            "user_id": card.user_id,
            "name": card.name,
            "age": card.age,
            "city": card.city,
            "sex": card.sex.value,
            "interests": card.interests,
            "description": card.description
        }


    def _compose_media_dict(self, media: Media, card_id: int) -> dict:
        return {
            "id": media.file_id,
            "card_id": card_id,
            "type": media.type
        }
