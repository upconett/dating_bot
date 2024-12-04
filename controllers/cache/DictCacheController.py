from typing import Any
from controllers.cache import CacheController

class DictCacheController(CacheController):
    def __init__(self):
        self.cache = {}


    async def get_data(self, key: str) -> dict | None:
        return self.cache.get(key)


    async def get_inner(self, key: str, inner_key: str) -> Any | None:
        data = self.cache.get(key)
        if data is dict:
            return data.get(inner_key)
        return None


    async def set_data(self, key: str, data: dict) -> None:
        self.cache[key] = data

    
    async def set_inner(self, key: str, inner_key: str, value: Any) -> bool:
        data = self.cache.get(key)
        if data is None:
            return False
        data[inner_key] = value
        self.cache[key] = data
        return True
