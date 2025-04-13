import pytest_asyncio
from models import Base
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from tests.functional.settings import settings


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def prepare_database():
    engine_test = create_async_engine(
        settings.postgres_url,
        future=True,
        connect_args={"prepared_statement_cache_size": 0},
    )
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine_test
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()


@pytest_asyncio.fixture(loop_scope="function")
async def db_session(prepare_database):
    test_sessionmaker = async_sessionmaker(
        bind=prepare_database, expire_on_commit=False, class_=AsyncSession
    )
    async with test_sessionmaker() as session:
        yield session
        await session.rollback()
