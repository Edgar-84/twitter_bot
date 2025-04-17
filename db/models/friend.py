from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from db.crud import AsyncCRUD
from db.engine import Base
from sqlalchemy import select


class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    friend_profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)

    __table_args__ = (UniqueConstraint("profile_id", "friend_profile_id"),)


class FriendCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Friend)

    # async def add_friends(self, profile_id, friend_ids):
    #     async with self._get_session() as session:
    #         for friend_id in friend_ids:
    #             exists = await session.execute(
    #                 select(Friend).where(
    #                     Friend.profile_id == profile_id,
    #                     Friend.friend_profile_id == friend_id
    #                 )
    #             )
    #             if not exists.scalars().first():
    #                 session.add(Friend(profile_id=profile_id, friend_profile_id=friend_id))
    #         await session.commit()

    async def add_friends(self, profile_id, friend_ids):
        async with self._get_session() as session:
            for friend_id in friend_ids:
                if profile_id == friend_id:
                    continue  # Missed adding self
                exists = await session.execute(
                    select(Friend).where(
                        Friend.profile_id == profile_id,
                        Friend.friend_profile_id == friend_id
                    )
                )
                if not exists.scalars().first():
                    session.add(Friend(profile_id=profile_id, friend_profile_id=friend_id))
            await session.commit()

    async def get_friends(self, profile_id):
        async with self._get_session() as session:
            result = await session.execute(select(Friend.friend_profile_id).where(Friend.profile_id == profile_id))
            return [r[0] for r in result.all()]
