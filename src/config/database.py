from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from . import settings

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
)

session_factory = async_sessionmaker(bind=engine)


class Base(DeclarativeBase):
    def __repr__(self):
        return self.__class__.__name__
