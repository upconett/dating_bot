from logic import CardWriter
from models import Card, Sex


class CardService:
    card_writer: CardWriter


    def __init__(self, card_writer: CardWriter):
        self.card_writer = card_writer


    async def create(self, card_data: dict, user_id: int) -> Card:
        card = self._card_from_data(card_data, user_id)
        await self.card_writer.create(card)
        return card

    
    def _card_from_data(self, card_data: dict, user_id: int) -> Card:
        return Card(
            id=card_data.get("id"),
            user_id=user_id,
            name=card_data.get("name"),
            sex=Sex(card_data.get("sex")),
            age=card_data.get("age"),
            city=card_data.get("city"),
            interests=card_data.get("interests"),
            description=card_data.get("description"),
            media=None
        )