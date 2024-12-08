from typing import Any, List, Dict
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.future import select as orm_select
from sqlalchemy import update as orm_update, delete as orm_delete, Result
from sqlalchemy import Column, DateTime, func

from controllers.database import DBController

from .Base import Base
from .models import *



class SQLAlchemyController(DBController):
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.base_model = Base
        

    def _get_model(self, table: str):
        """Возвращает ORM-класс для указанной таблицы"""
        for cls in self.base_model.__subclasses__():
            if cls.__tablename__ == table:
                return cls
        raise ValueError(f"No model found for table '{table}'")

    
    async def select(self, table: str, filter_by: Dict[str, Any]) -> List[Dict]:
        async with self.async_session() as session:
            model = self._get_model(table)
            query = orm_select(model)
            if filter_by:
                query = query.filter_by(**filter_by)
            result: Result = await session.execute(query)
            return [row._asdict() for row in result.scalars().all()]


    async def insert(self, table: str, data: Dict[str, Any]) -> bool:
        async with self.async_session() as session:
            model = self._get_model(table)
            instance = model(**data)
            session.add(instance)
            await session.commit()
            return True


    async def update(self, table: str, filter_by: Dict[str, Any], data: Dict[str, Any]) -> bool:
        async with self.async_session() as session:
            model = self._get_model(table)
            query = orm_update(model).where(
                *[
                    getattr(model, key) == value
                    for key, value in filter_by.items()
                ]
            ).values(**data)
            await session.execute(query)
            await session.commit()
            return True


    async def delete(self, table: str, filter_by: Dict[str, Any]) -> bool:
        async with self.async_session() as session:
            model = self._get_model(table)
            query = orm_delete(model).where(
                *[
                    getattr(model, key) == value
                    for key, value in filter_by.items()
                ]
            )
            await session.execute(query)
            await session.commit()
            return True


    async def custom_query(self, query: str) -> List[Dict] | bool:
        async with self.async_session() as session:
            result: Result = await session.execute(query)
            try:
                return [dict(row) for row in result.fetchall()]
            except Exception:
                await session.commit()
                return True
