import pytest_asyncio
from models import Role
from tests.functional.fixtures.postgres import db_session


@pytest_asyncio.fixture(loop_scope="function")
async def create_roles(db_session):
    roles = []
    for i in ["user", "admin"]:
        role = Role(title=i)
        roles.append(role)
    db_session.add_all(roles)
    await db_session.commit()
    return roles
