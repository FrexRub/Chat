import asyncio
from typing import AsyncGenerator, Generator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

from src.main import app
from src.core.database import Base, get_async_session

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///test.sqlite3"


@pytest_asyncio.fixture(loop_scope="session", scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Создаем экземпляр цикла обработки событий для каждого тестового примера.
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine: AsyncEngine = create_async_engine(SQLALCHEMY_DATABASE_URL)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_session] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
