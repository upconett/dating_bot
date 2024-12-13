from typing import Any, List, Dict
from abc import ABC, abstractmethod


class DBController(ABC):
    @abstractmethod
    async def select(self, table: str, filter_by: Dict[str, Any]) -> List[Dict]:
        ...

    @abstractmethod
    async def insert(self, table: str, data: Dict[str, Any]) -> bool:
        ...

    @abstractmethod
    async def update(self, table: str, filter_by: Dict[str, Any], data: Dict[str, Any]) -> bool:
        ...

    @abstractmethod
    async def delete(self, table: str, filter_by: Dict[str, Any]) -> bool:
        ...

    @abstractmethod
    async def custom_query(self, query: str) -> List[Dict] | bool:
        ...
