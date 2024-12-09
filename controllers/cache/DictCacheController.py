from typing import Any
from controllers.cache import CacheController

from controllers.exceptions import *

class DictCacheController(CacheController):
    def __init__(self):
        self.cache = {}


    async def get_data(self, key: str) -> dict:
        data = self.cache.get(key)
        if data is None: raise NoDataInCache()
        return data


    async def get_inner(self, key: str, inner_key: str) -> Any:
        data = self.cache.get(key)
        if data is dict:
            return data.get(inner_key)
        if data is None: raise NoDataInCache()


    async def set_data(self, key: str, data: dict) -> None:
        self.cache[key] = data

    
    async def set_inner(self, key: str, inner_key: str, value: Any) -> bool:
        data = self.cache.get(key)
        if data is None:
            return False
        data[inner_key] = value
        self.cache[key] = data
        return True


    async def remove_key(self, key: str) -> None:
        self.cache.pop(key, None)
