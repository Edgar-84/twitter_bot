from sqlalchemy import (
    Column, Integer, select, ForeignKey, DateTime, func
)
from db.crud import AsyncCRUD
from db.engine import Base
from datetime import datetime, timezone


class SearchSession(Base):
    __tablename__ = "search_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("search_algorithms.id"), nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = Column(DateTime, nullable=True)


class SearchSessionCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(SearchSession)

    async def create_session(self, user_id, profile_id, algorithm_id):
        async with self._get_session() as session:
            session_obj = SearchSession(
                user_id=user_id, profile_id=profile_id, algorithm_id=algorithm_id
            )
            session.add(session_obj)
            await session.commit()
            await session.refresh(session_obj)
            return session_obj

    async def get_user_sessions(self, user_id):
        async with self._get_session() as session:
            result = await session.execute(select(SearchSession).where(SearchSession.user_id == user_id))
            return result.scalars().all()
