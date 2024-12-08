from logic.abstract.user import UserLoader

from models import User

from logic.exceptions import *

class DefaultUserLoader(UserLoader):
    async def get_by_tg_id(self, tg_id: int):
        result = await self.db.select("users", filter_by={"tg_id": tg_id})
        if len(result) == 0:
            raise


    async def get_by_internal_id(self, internal_id: int):
        
