from sqlalchemy import (
    Column, Integer, String, select, ForeignKey, Boolean, DateTime, func
)
from db.crud import AsyncCRUD
from db.engine import Base
from datetime import datetime, timezone, date


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, index=True, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    chosen_language = Column(String, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserRequest(Base):
    __tablename__ = "user_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class UserCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(User)

    async def get_admin(self):
        async with self._get_session() as session:
            admin = await session.execute(select(self.model).where(self.model.role_id.is_(1)))
            if admin:
                return admin.scalars().first()

    async def set_status(self, user_id, status_type, value):
        async with self._get_session() as session:
            user = await session.execute(select(self.model).where(self.model.id.is_(user_id)))
            user = user.scalars().first()
            if user:
                if status_type == 'approved':
                    user.approved = value
                elif status_type == 'is_on_work_shift':
                    user.is_on_work_shift = value
                await session.commit()
                await session.refresh(user)
                return user
            return

    async def get_by_number(self, phone):
        async with self._get_session() as session:
            user = await session.execute(select(self.model).where(self.model.phone.is_(phone)))
            return user.scalars().first()


class UserRequestCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(UserRequest)

    async def save_request(self, user_id: int):
        async with self._get_session() as session:
            request = UserRequest(user_id=user_id)
            session.add(request)
            await session.commit()
            await session.refresh(request)
            return request
    
    async def get_requests_count(self, user_id: int) -> int:
        async with self._get_session() as session:
            today = date.today()
            start_of_day = datetime(today.year, today.month, today.day)
            
            query = select(func.count()).where(
                UserRequest.user_id == user_id,
                UserRequest.timestamp >= start_of_day
            )
            result = await session.execute(query)
            return result.scalar()
    
    async def get_daily_requests_summary(self) -> dict:
        async with self._get_session() as session:
            today = date.today()
            start_of_day = datetime(today.year, today.month, today.day)
            
            query = select(UserRequest.user_id, func.count()).where(
                UserRequest.timestamp >= start_of_day
            ).group_by(UserRequest.user_id)
            
            result = await session.execute(query)
            return {row[0]: row[1] for row in result.fetchall()}


# TODO divide on separated models and services

# from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
# from sqlalchemy.orm import relationship
# from datetime import datetime, timezone
# from base import Base

# -----------------------------
# Models
# -----------------------------

# class Profile(Base):
#     __tablename__ = "profiles"

#     id = Column(Integer, primary_key=True)
#     username = Column(String, unique=True, index=True, nullable=False)
#     full_name = Column(String, nullable=True)
#     last_checked = Column(DateTime, nullable=True)


# class Friend(Base):
#     __tablename__ = "friends"

#     id = Column(Integer, primary_key=True)
#     profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
#     friend_profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)

#     __table_args__ = (UniqueConstraint("profile_id", "friend_profile_id"),)


# class Post(Base):
#     __tablename__ = "posts"

#     id = Column(Integer, primary_key=True)
#     profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
#     content = Column(Text, nullable=False)
#     timestamp = Column(DateTime, nullable=False, index=True)
#     retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


# class SearchAlgorithm(Base):
#     __tablename__ = "search_algorithms"

#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     friends_limit = Column(Integer, nullable=True)
#     hours_limit = Column(Integer, nullable=False)
#     created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


# class SearchSession(Base):
#     __tablename__ = "search_sessions"

#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
#     algorithm_id = Column(Integer, ForeignKey("search_algorithms.id"), nullable=False)
#     started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
#     finished_at = Column(DateTime, nullable=True)


# # TODO delete
# class SearchSessionFriend(Base):
#     __tablename__ = "search_session_friends"

#     id = Column(Integer, primary_key=True)
#     session_id = Column(Integer, ForeignKey("search_sessions.id"), nullable=False)
#     friend_profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)


# class Summary(Base):
#     __tablename__ = "summaries"

#     id = Column(Integer, primary_key=True)
#     session_id = Column(Integer, ForeignKey("search_sessions.id"), nullable=False)
#     summary_text = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


# TODO services

# from sqlalchemy import select
# from sqlalchemy.orm import joinedload
# from models import (
#     Profile, Friend, Post, SearchAlgorithm,
#     SearchSession, SearchSessionFriend, Summary
# )
# from async_crud_base import AsyncCRUD
# from datetime import datetime, timedelta


# class ProfileCRUD(AsyncCRUD):
#     def __init__(self):
#         super().__init__(Profile)

#     async def get_or_create_by_username(self, username):
#         async with self._get_session() as session:
#             result = await session.execute(select(Profile).where(Profile.username == username))
#             profile = result.scalars().first()
#             if profile:
#                 return profile
#             profile = Profile(username=username)
#             session.add(profile)
#             await session.commit()
#             await session.refresh(profile)
#             return profile

#     async def update_last_checked(self, profile_id):
#         async with self._get_session() as session:
#             profile = await session.get(Profile, profile_id)
#             if profile:
#                 profile.last_checked_at = datetime.utcnow()
#                 await session.commit()
#                 await session.refresh(profile)
#                 return profile

#     async def get_by_username(self, username):
#         async with self._get_session() as session:
#             result = await session.execute(select(Profile).where(Profile.username == username))
#             return result.scalars().first()


# class FriendCRUD(AsyncCRUD):
#     def __init__(self):
#         super().__init__(Friend)

#     async def add_friends(self, profile_id, friend_ids):
#         async with self._get_session() as session:
#             for friend_id in friend_ids:
#                 exists = await session.execute(
#                     select(Friend).where(
#                         Friend.profile_id == profile_id,
#                         Friend.friend_profile_id == friend_id
#                     )
#                 )
#                 if not exists.scalars().first():
#                     session.add(Friend(profile_id=profile_id, friend_profile_id=friend_id))
#             await session.commit()

#     async def get_friends(self, profile_id):
#         async with self._get_session() as session:
#             result = await session.execute(select(Friend.friend_profile_id).where(Friend.profile_id == profile_id))
#             return [r[0] for r in result.all()]


# class PostCRUD(AsyncCRUD):
#     def __init__(self):
#         super().__init__(Post)

#     async def add_posts(self, profile_id, posts):
#         async with self._get_session() as session:
#             for post in posts:
#                 post_obj = Post(profile_id=profile_id, content=post['content'], timestamp=post['timestamp'])
#                 session.add(post_obj)
#             await session.commit()

#     async def get_recent_posts(self, profile_id, since_hours):
#         async with self._get_session() as session:
#             since_time = datetime.utcnow() - timedelta(hours=since_hours)
#             result = await session.execute(
#                 select(Post).where(Post.profile_id == profile_id, Post.timestamp >= since_time)
#             )
#             return result.scalars().all()

#     async def get_all_recent_posts(self, profile_ids, since_hours):
#         async with self._get_session() as session:
#             since_time = datetime.utcnow() - timedelta(hours=since_hours)
#             result = await session.execute(
#                 select(Post).where(Post.profile_id.in_(profile_ids), Post.timestamp >= since_time)
#             )
#             return result.scalars().all()


# class SearchAlgorithmCRUD(AsyncCRUD):
#     def __init__(self):
#         super().__init__(SearchAlgorithm)

#     async def create_algorithm(self, name, friends_limit, hours_limit):
#         async with self._get_session() as session:
#             algo = SearchAlgorithm(name=name, friends_limit=friends_limit, hours_limit=hours_limit)
#             session.add(algo)
#             await session.commit()
#             await session.refresh(algo)
#             return algo

#     async def get_latest(self):
#         async with self._get_session() as session:
#             result = await session.execute(select(SearchAlgorithm).order_by(SearchAlgorithm.created_at.desc()))
#             return result.scalars().first()


# class SearchSessionCRUD(AsyncCRUD):
#     def __init__(self):
#         super().__init__(SearchSession)

#     async def create_session(self, user_id, profile_id, algorithm_id):
#         async with self._get_session() as session:
#             session_obj = SearchSession(
#                 user_id=user_id, profile_id=profile_id, algorithm_id=algorithm_id
#             )
#             session.add(session_obj)
#             await session.commit()
#             await session.refresh(session_obj)
#             return session_obj

#     async def get_user_sessions(self, user_id):
#         async with self._get_session() as session:
#             result = await session.execute(select(SearchSession).where(SearchSession.user_id == user_id))
#             return result.scalars().all()

## TODO delete
# class SearchSessionFriendCRUD(AsyncCRUD):
#     def __init__(self):
#         super().__init__(SearchSessionFriend)

#     async def add_friends_to_session(self, session_id, friend_ids):
#         async with self._get_session() as session:
#             for fid in friend_ids:
#                 session.add(SearchSessionFriend(session_id=session_id, friend_profile_id=fid))
#             await session.commit()

#     async def get_session_friends(self, session_id):
#         async with self._get_session() as session:
#             result = await session.execute(
#                 select(SearchSessionFriend.friend_profile_id).where(SearchSessionFriend.session_id == session_id)
#             )
#             return [r[0] for r in result.all()]


# class SummaryCRUD(AsyncCRUD):
#     def __init__(self):
#         super().__init__(Summary)

#     async def create_summary(self, session_id, summary_text):
#         async with self._get_session() as session:
#             summary = Summary(session_id=session_id, summary_text=summary_text)
#             session.add(summary)
#             await session.commit()
#             await session.refresh(summary)
#             return summary

#     async def get_by_session(self, session_id):
#         async with self._get_session() as session:
#             result = await session.execute(select(Summary).where(Summary.session_id == session_id))
#             return result.scalars().first()
