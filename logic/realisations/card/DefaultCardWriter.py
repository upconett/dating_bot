from logic import CardWriter

from models import Card


class DefaultCardWriter(CardWriter):

    async def create(self, card: Card):
        await self.db.insert(
            table="cards",
            data={
                "user_id": card.user_id,
                "name": card.name,
                "age": card.age,
                "city": card.city,
                "sex": card.sex.value,
                "interests": card.interests,
                "description": card.description
            }
        )


    async def update(self, card: Card):
        await self.db.update(
            table="cards",
            filter_by={
                "id": card.id,
            },
            data=card.__dict__
        )


    async def delete(self, card: Card):
        await self.db.delete(
            table="cards",
            filter_by={
                "id": card.id
            }
        )
