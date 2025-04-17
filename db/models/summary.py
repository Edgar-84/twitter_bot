from sqlalchemy import (
    Column, Integer, select, Text, ForeignKey, DateTime, func
)
from db.crud import AsyncCRUD
from db.engine import Base
from datetime import datetime, timezone


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("search_sessions.id"), nullable=False)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)



class SummaryCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Summary)

    async def create_summary(self, session_id, summary_text):
        async with self._get_session() as session:
            summary = Summary(session_id=session_id, summary_text=summary_text)
            session.add(summary)
            await session.commit()
            await session.refresh(summary)
            return summary

    async def get_by_session(self, session_id):
        async with self._get_session() as session:
            result = await session.execute(select(Summary).where(Summary.session_id == session_id))
            return result.scalars().first()
