from logic.abstract.user import UserLoader

from models import User

from logic.exceptions import *
from controllers.exceptions import *

from logic.static import UserAdapter


class DefaultUserLoader(UserLoader):

    async def get_by_tg_id(self, tg_id: int) -> User:
        try:
            return await self._load_from_cache(tg_id)
        except NoDataInCache:
            user = await self._load_from_db_by_tg_id(tg_id)
            await self._place_in_cache(user)
            return user
    

    async def get_by_internal_id(self, internal_id: int) -> User:
        try:
            tg_id = await self._load_tg_id_from_cache(internal_id)
            return await self._load_from_cache(tg_id)
        except NoDataInCache:
            user = await self._load_from_db_by_internal_id(internal_id)
            await self._place_in_cache(user)
            return user


    async def remove_from_cache(self, tg_id: int, internal_id: int):
        await self.cache.remove_key(f"tg_id:{tg_id}")
        await self.cache.remove_key(f"internal_id:{internal_id}")

        
    async def _load_tg_id_from_cache(self, internal_id: int) -> int:
        return await self.cache.get_data(f"id:{internal_id}")


    async def _load_from_cache(self, tg_id: int) -> User:
        data_from_cache = await self.cache.get_data(f"tg_id:{tg_id}")
        return UserAdapter.from_dict(data_from_cache)

    
    async def _load_from_db_by_tg_id(self, tg_id: int) -> User:
        db_result_user = await self.db.select("users", filter_by={"tg_id": tg_id})
        db_result_settings = await self.db.select("settings", filter_by={"user_id": tg_id})
        if len(db_result_user) == 0: raise UserNotFound()
        data_from_db = db_result_user[0]
        print(db_result_settings)
        if db_result_settings:
            data_from_db['settings'] = db_result_settings[0]
        return UserAdapter.from_dict(data_from_db)


    async def _load_from_db_by_internal_id(self, internal_id: int) -> User:
        db_result = await self.db.select("users", filter_by={"id": internal_id})
        if len(db_result) == 0: raise UserNotFound()
        data_from_db = db_result[0]
        db_result_settings = await self.db.select("settings", filter_by={"user_id": data_from_db.get("id")})
        print(db_result_settings)
        if db_result_settings:
            data_from_db['settings'] = db_result_settings[0]
        return UserAdapter.from_dict(data_from_db)

    
    async def _place_in_cache(self, user: User):
        user_data = UserAdapter.to_dict(user)
        await self.cache.set_data(f"tg_id:{user.tg_id}", user_data)
        await self.cache.set_data(f"id:{user.id}", user.tg_id)
