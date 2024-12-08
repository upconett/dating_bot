from abc import ABC, abstractmethod

from controllers import DBController, CacheController

from models import Card


class CardWriter(ABC):
    db: DBController
    cache: CacheController

    
    def __init__(self, db_controller: DBController, cache_controller: CacheController):
        self.db = db_controller
        self.cache = cache_controller


    @abstractmethod
    async def create(self, card: Card) -> None:
        ...

    @abstractmethod
    async def update(self, card: Card) -> None:
        ...
    
    @abstractmethod
    async def delete(self, card: Card) -> None:
        ...
