from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime, timezone, timedelta
from db.engine import Base
from db.crud import AsyncCRUD


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    content = Column(Text, nullable=False)
    post_url = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class PostCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Post)

    async def add_posts(self, profile_id, posts):
        async with self._get_session() as session:
            for post in posts:
                post_obj = Post(profile_id=profile_id, content=post['content'], post_url=post['url'], timestamp=post['timestamp'])
                session.add(post_obj)
            await session.commit()

    async def get_recent_posts(self, profile_id, since_hours):
        async with self._get_session() as session:
            since_time = datetime.now(timezone.utc) - timedelta(hours=since_hours)
            result = await session.execute(
                select(Post).where(Post.profile_id == profile_id, Post.timestamp >= since_time)
            )
            return result.scalars().all()

    async def get_all_recent_posts(self, profile_ids, since_hours):
        async with self._get_session() as session:
            since_time = datetime.now(timezone.utc) - timedelta(hours=since_hours)
            result = await session.execute(
                select(Post).where(Post.profile_id.in_(profile_ids), Post.timestamp >= since_time)
            )
            return result.scalars().all()
