import asyncio
from db.engine import engine, Base
from db.models.user import User, UserRequest  # don`t remove this import
from db.models.profile import Profile
from db.models.search_session import SearchSession
from db.models.search_algorithm import SearchAlgorithm
from db.models.summary import Summary
from db.models.post import Post

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
