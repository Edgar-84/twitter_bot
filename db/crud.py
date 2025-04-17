from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from db.session import Sessions


class AsyncCRUD:
    def __init__(self, model):
        self.model = model

    @asynccontextmanager
    async def _get_session(self) -> AsyncSession:
        """Context manager to get the session."""
        async for session in Sessions.get_session():
            yield session

    async def create(self, **kwargs):
        async with self._get_session() as session:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.commit()
            return instance

    async def read(self, id_):
        async with self._get_session() as session:
            query = select(self.model).where(self.model.id.is_(id_))
            result = await session.execute(query)
            try:
                return result.scalars().one()
            except NoResultFound:
                return None

    async def update(self, id_, **kwargs):
        async with self._get_session() as session:
            query = select(self.model).where(self.model.id.is_(id_))
            result = await session.execute(query)
            try:
                instance = result.scalars().one()
                for attr, value in kwargs.items():
                    setattr(instance, attr, value)
                await session.commit()
                await session.refresh(instance)
                return instance
            except NoResultFound:
                return None

    async def delete(self, id_):
        async with self._get_session() as session:
            query = select(self.model).where(self.model.id.is_(id_))
            result = await session.execute(query)
            try:
                instance = result.scalars().one()
                await session.delete(instance)
                await session.commit()
            except NoResultFound:
                return None

    async def get_all(self):
        async with self._get_session() as session:
            query = select(self.model)
            result = await session.execute(query)
            return result.scalars().all()
