import pytest_asyncio
from models import Base
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from tests.functional.settings import settings


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(settings.postgres_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = async_sessionmaker(
            bind=conn, expire_on_commit=False, class_=AsyncSession
        )()
        yield session
        await session.close()
        await transaction.rollback()
