import pytest_asyncio
from db.postgres import get_postgres_session
from httpx import AsyncClient
from main import app
from tests.functional.settings import settings


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_postgres_session] = override_get_db
    async with AsyncClient(base_url=settings.service_url) as client:
        yield client
