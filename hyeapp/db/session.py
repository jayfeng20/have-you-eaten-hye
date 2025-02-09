from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from core.config import db_configuration

# Create the connection URL.
url_object = URL.create(
    drivername="postgresql+asyncpg",
    username=db_configuration.DB_USERNAME,
    password=db_configuration.DB_PASSWORD,
    host=db_configuration.DB_HOST,
    port=db_configuration.DB_PORT,
    database=db_configuration.DB_NAME,
)

# Create async engine.
engine = create_async_engine(url_object, echo=True)

# Create async session factory.
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for obtaining a DB session.
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
