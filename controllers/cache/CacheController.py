from typing import Any
from abc import ABC, abstractmethod

class CacheController(ABC):
    
    @abstractmethod
    async def get_data(self, key: str) -> dict:
        ...

    @abstractmethod
    async def set_data(self, key: str, data: dict) -> None:
        ...

    @abstractmethod
    async def get_inner(self, key: str, inner_key: str) -> Any:
        ...

    async def set_inner(self, key: str, inner_key: str, value: Any) -> bool:
        ...

    @abstractmethod
    async def remove_key(self, key: str) -> None:
        ...
