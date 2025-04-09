from uuid import uuid4

import pytest_asyncio
from models import User
from tests.functional.fixtures.postgres import db_session


@pytest_asyncio.fixture(loop_scope="session")
async def create_users(db_session):
    users = []
    for i in range(3):
        user = User(
            login=f"Login_{i}",
            password=f"password_{i}",
            first_name=f"First_{i}",
            last_name=f"Last_{i}",
        )
        user.id = uuid4()
        users.append(user)
    db_session.add_all(users)
    await db_session.commit()
    return users
