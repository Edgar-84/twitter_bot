from sqlalchemy import (
    Column, Integer, String, select, DateTime, func
)
from db.crud import AsyncCRUD
from db.engine import Base
from datetime import datetime, timezone


class SearchAlgorithm(Base):
    __tablename__ = "search_algorithms"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    friends_limit = Column(Integer, nullable=True)
    hours_limit = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class SearchAlgorithmCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(SearchAlgorithm)

    async def create_algorithm(self, name, friends_limit, hours_limit):
        async with self._get_session() as session:
            algo = SearchAlgorithm(name=name, friends_limit=friends_limit, hours_limit=hours_limit)
            session.add(algo)
            await session.commit()
            await session.refresh(algo)
            return algo

    async def get_latest(self):
        async with self._get_session() as session:
            result = await session.execute(select(SearchAlgorithm).order_by(SearchAlgorithm.created_at.desc()))
            return result.scalars().first()
