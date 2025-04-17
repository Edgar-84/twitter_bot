import logging
from bot.settings import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
