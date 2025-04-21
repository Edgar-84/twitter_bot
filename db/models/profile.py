from sqlalchemy import (
    Column, Integer, String, select, DateTime, func
)
from db.crud import AsyncCRUD
from db.engine import Base
from datetime import datetime, timezone


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    twitter_id = Column(Integer, nullable=False)
    followers_count = Column(Integer, nullable=True)
    last_checked = Column(DateTime, nullable=True)


class ProfileCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Profile)

    async def get(self, profile_id: int) -> Profile | None:
        async with self._get_session() as session:
            return await session.get(Profile, profile_id)

    async def create(self, username: str, twitter_id: int, followers_count: int = None):
        async with self._get_session() as session:
            profile = Profile(username=username, twitter_id=twitter_id, followers_count=followers_count)
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            return profile

    # async def get_or_create_by_username(self, username: str):
        # async with self._get_session() as session:
        #     result = await session.execute(select(Profile).where(Profile.username == username))
        #     profile = result.scalars().first()
        #     if profile:
        #         return profile
        #     profile = Profile(username=username)
        #     session.add(profile)
        #     await session.commit()
        #     await session.refresh(profile)
        #     return profile
        #     if profile:
        #         return profile
        #     profile = Profile(username=username, twitter_id=twitter_id)
        #     session.add(profile)
        #     await session.commit()
        #     await session.refresh(profile)
        #     return profile

    async def update_last_checked(self, profile_id: int):
        async with self._get_session() as session:
            profile = await session.get(Profile, profile_id)
            if profile:
                profile.last_checked_at = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(profile)
                return profile

    async def get_by_username(self, username: str):
        async with self._get_session() as session:
            result = await session.execute(select(Profile).where(Profile.username == username))
            return result.scalars().first()

    async def bulk_save_profiles(self, profiles: list[dict]) -> list[int]:
        async with self._get_session() as session:
            # Get already existing username
            usernames = [p["username"] for p in profiles]
            result = await session.execute(select(Profile).where(Profile.username.in_(usernames)))
            existing_profiles = {p.username: p.id for p in result.scalars().all()}

            new_profiles = []
            for profile in profiles:
                if profile["username"] not in existing_profiles:
                    new_profiles.append(Profile(
                        username=profile["username"],
                        full_name=profile.get("full_name"),
                        twitter_id=profile["twitter_id"]
                    ))

            if new_profiles:
                session.add_all(new_profiles)
                await session.commit()

            # Get all again — including just added
            result = await session.execute(select(Profile).where(Profile.username.in_(usernames)))
            all_profiles = {p.username: p.id for p in result.scalars().all()}
            return [all_profiles[p["username"]] for p in profiles]
