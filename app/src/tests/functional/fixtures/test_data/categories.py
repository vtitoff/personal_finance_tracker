import pytest_asyncio
from models import IncomingCategory, OutgoingCategory
from tests.functional.fixtures.postgres import db_session


@pytest_asyncio.fixture(loop_scope="session")
async def create_outgoing_categories(db_session):
    categories = []
    for i in range(10):
        category = OutgoingCategory(
            name=f"Test Category {i}",
            description=f"Description {i}",
        )
        categories.append(category)
    db_session.add_all(categories)
    await db_session.commit()
    return categories
