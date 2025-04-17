from asyncio import current_task
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session
from sqlalchemy.orm import sessionmaker
from bot.settings import DATABASE_URL


class Sessions:
    ENGINE = None

    @classmethod
    def __check_engine(cls):
        if not cls.ENGINE:
            cls.ENGINE = create_async_engine(DATABASE_URL, future=True, echo=False)

    @classmethod
    async def get_session(cls) -> AsyncSession:
        cls.__check_engine()
        async_session = sessionmaker(cls.ENGINE, class_=AsyncSession, expire_on_commit=False, autoflush=False)
        async with async_session() as session:
            yield session

    @classmethod
    def get_scoped_session(cls):
        cls.__check_engine()
        scoped_session = async_scoped_session(sessionmaker(cls.ENGINE, class_=AsyncSession, expire_on_commit=False),
                                              current_task)
        return scoped_session()
