from logic import CardWriter
from models import Card, Sex


class CardService:
    card_writer: CardWriter


    def __init__(self, card_writer: CardWriter):
        self.card_writer = card_writer


    async def create(self, card: Card) -> Card:
        await self.card_writer.create(card)
        return card

    
