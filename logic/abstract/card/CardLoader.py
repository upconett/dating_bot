from abc import ABC, abstractmethod

from controllers import DBController, CacheController

from models import Card, User


class CardLoader(ABC):
    db: DBController
    cache: CacheController
    
    def __init__(self, db_controller: DBController, cache_controller: CacheController):
        self.db = db_controller
        self.cache = cache_controller

    @abstractmethod
    async def get_recomended(self, user: User, limit: int = 50) -> Card:
        ...

    @abstractmethod
    async def get_by_id(self, id: int) -> Card:
        ...

    @abstractmethod
    async def make_all_cards_as_unseen(self, user: User) -> None:
        ...
