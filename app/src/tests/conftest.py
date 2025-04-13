import asyncio

import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
async def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.stop()
    loop.close()


pytest_plugins = [
    "tests.functional.fixtures.postgres",
    "tests.functional.fixtures.redis",
    "tests.functional.fixtures.auth",
    "tests.functional.fixtures.async_client",
    "tests.functional.fixtures.test_data.categories",
    "tests.functional.fixtures.test_data.transactions",
    "tests.functional.fixtures.test_data.users",
    "tests.functional.fixtures.test_data.roles",
    "tests.functional.fixtures.test_data.wallets",
]
