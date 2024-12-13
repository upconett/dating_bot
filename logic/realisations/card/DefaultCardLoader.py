from typing import List

from controllers import DBController, CacheController
from logic import CardLoader
from models import Card, Settings, User

from controllers.exceptions import NoDataInCache
from logic.exceptions import CardNotFound

from logic.static import CardAdapter

from . import queries


class DefaultCardLoader(CardLoader):
    db: DBController
    cache: CacheController

    async def get_recomended(self, user: User, limit: int = 50) -> Card:
        try:
            pool: List[int] = await self.cache.get_inner(
                f"tg_id:{user.tg_id}", "recomendation_pool"
            )
            if not pool: raise NoDataInCache()
            card_id = pool.pop(0)
            await self.cache.set_inner(f"tg_id:{user.tg_id}", "recomendation_pool", pool)

            card = await self.get_by_id(card_id)
            # print("From Cache")
            return card
        except NoDataInCache:
            user_card = await self.get_by_id(user.id)
            pool = (
                await self._get_by_full_recomendation(user, user_card, limit)
                or await self._get_from_other_cities(user, user_card, limit)
                or await self._get_of_different_age(user, user_card, limit)
                or await self._get_of_different_age_from_other_cities(user, user_card, limit)
                or await self._get_regardless_of_interests(user, user_card, limit)
                or await self._get_by_sex(user, user_card, limit)
                or await self._get_rest_of_cards(user, limit)
            )
            if not pool: raise CardNotFound()
            await self._update_seen_cards(user, pool)

            card_id = pool.pop(0)
            await self.cache.set_inner(f"tg_id:{user.tg_id}", "recomendation_pool", pool)
            card = await self.get_by_id(card_id)
            # print("From DB")
            return card
            

    async def get_by_id(self, id: int) -> Card:
        result = await self.db.select(
            table="cards",
            filter_by={"id": id },
        )
        if not result: raise CardNotFound()
        card_data = result[0]
        media_data = await self.db.select(
            table="card_media",
            filter_by={"card_id": id },
        )
        return CardAdapter.from_dict(card_data, media_data)
    

    async def get_by_user_id(self, user_id: int) -> Card:
        result = await self.db.select(
            table="cards",
            filter_by={"user_id": user_id },
        )
        if not result: raise CardNotFound()
        card_data = result[0]
        media_data = await self.db.select(
            table="card_media",
            filter_by={"card_id": card_data.get("id")},
        )
        return CardAdapter.from_dict(card_data, media_data)

    
    async def make_all_cards_as_unseen(self, user: User):
        result = await self.db.select(table="seen_cards", filter_by={"user_id": user.tg_id})
        if not result: return
        
        bit_string: str = result[0]["bit_string"]
        await self.db.update(
            table="seen_cards", filter_by={"user_id": user.tg_id}, data={"bit_string": '0'*len(bit_string)}
        )


    async def _update_seen_cards(self, user: User, recomendation_pool: List[int]):
        bit_string = ""
        result = await self.db.select(table="seen_cards", filter_by={"user_id": user.tg_id})
        if result: bit_string: str = result[0]["bit_string"]
        else: return
        for card_id in recomendation_pool:
            bit_string = bit_string[:card_id-1] + '1' + bit_string[card_id:]
        await self.db.update(
            table="seen_cards", filter_by={"user_id": user.tg_id}, data={"bit_string": bit_string}
        )


    async def _get_by_full_recomendation(self, user: User, user_card: Card, limit: int) -> List[int]:
        result = await self.db.custom_query(
                queries.FULL_RECOMENDATION
                .format(
                    seek_sex=user.settings.seek_sex.value,
                    seek_age_from=user.settings.seek_age_from,
                    seek_age_to=user.settings.seek_age_to,
                    interests=user_card.interests,
                    target_city=user_card.city,
                    current_user_id=user_card.user_id,
                    current_id=user_card.id,
                    limit=limit,
                )
            )
        return [x[0] for x in result]
    
    async def _get_from_other_cities(self, user: User, user_card: Card, limit: int) -> List[int]:
        result = await self.db.custom_query(
                queries.RECOMENDATION_NO_CITY
                .format(
                    seek_sex=user.settings.seek_sex.value,
                    seek_age_from=user.settings.seek_age_from,
                    seek_age_to=user.settings.seek_age_to,
                    interests=user_card.interests,
                    current_user_id=user_card.user_id,
                    current_id=user_card.id,
                    limit=limit,
                )
            )
        return [x[0] for x in result]

    async def _get_of_different_age(self, user: User, user_card: Card, limit: int) -> List[int]:
        result = await self.db.custom_query(
                queries.RECOMENDATION_NO_AGE
                .format(
                    seek_sex=user.settings.seek_sex.value,
                    target_city=user_card.city,
                    interests=user_card.interests,
                    current_user_id=user_card.user_id,
                    current_id=user_card.id,
                    limit=limit,
                )
            )
        return [x[0] for x in result]

    async def _get_of_different_age_from_other_cities(self, user: User, user_card: Card, limit: int) -> List[int]:
        result = await self.db.custom_query(
                queries.RECOMENDATION_NO_CITY_AGE
                .format(
                    seek_sex=user.settings.seek_sex.value,
                    interests=user_card.interests,
                    current_user_id=user_card.user_id,
                    current_id=user_card.id,
                    limit=limit,
                )
            )
        return [x[0] for x in result]

    async def _get_regardless_of_interests(self, user: User, user_card: Card, limit: int) -> List[int]:
        result = await self.db.custom_query(
                queries.RECOMENDATION_NO_INTERESTS
                .format(
                    seek_sex=user.settings.seek_sex.value,
                    seek_age_from=user.settings.seek_age_from,
                    seek_age_to=user.settings.seek_age_to,
                    target_city=user_card.city,
                    current_user_id=user_card.user_id,
                    current_id=user_card.id,
                    limit=limit,
                )
            )
        return [x[0] for x in result]


    async def _get_by_sex(self, user: User, user_card: Card, limit: int) -> List[int]:
        result = await self.db.custom_query(
                queries.RECOMENDATION_BY_SEX
                .format(
                    seek_sex=user.settings.seek_sex.value,
                    current_user_id=user_card.user_id,
                    current_id=user_card.id,
                    limit=limit,
                )
            )
        return [x[0] for x in result]

    async def _get_rest_of_cards(self, user: User, limit: int) -> List[int]:
        result = await self.db.custom_query(
                queries.RECOMENDATION_UNSEEN
                .format(
                    current_user_id=user.tg_id,
                    current_id=user.id,
                    limit=limit,
                )
            )
        return [x[0] for x in result]