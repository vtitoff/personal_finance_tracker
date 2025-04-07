import pytest_asyncio
from models import Base
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from tests.functional.settings import settings

engine_test = create_async_engine(settings.postgres_url, future=True)
test_sessionmaker = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session")
async def db_session():
    async with test_sessionmaker() as session:
        yield session
