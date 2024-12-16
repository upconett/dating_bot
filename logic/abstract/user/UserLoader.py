from abc import ABC, abstractmethod

from controllers import DBController, CacheController

from models import User

from logic.exceptions import *


class UserLoader(ABC):
    db: DBController
    cache: CacheController


    def __init__(self, db_controller: DBController, cache_controller: CacheController):
        self.db = db_controller
        self.cache = cache_controller


    @abstractmethod
    async def get_by_tg_id(self, tg_id: int) -> User:
        ...

    
    @abstractmethod
    async def get_by_internal_id(self, internal_id: int) -> User:
        ...

    @abstractmethod
    async def remove_from_cache(self, tg_id: int, internal_id: int):
        ...

    
    async def exists_by_tg_id(self, tg_id: int) -> User:
        try:
            self.get_by_tg_id(tg_id)
            return True
        except UserNotFound:
            return False
