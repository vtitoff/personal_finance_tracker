from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

import jwt
import pytest_asyncio
from tests.functional.settings import settings
from utils.auth import AccessTokenPayload


def auth_header(user_roles: List[str], user_id: str = None) -> dict[str, str]:
    user_id = user_id or str(uuid4())
    valid_till = datetime.now() + timedelta(hours=settings.access_token_exp_hours)
    payload = AccessTokenPayload(
        user_id=user_id, roles=user_roles, exp=int(valid_till.timestamp())
    )

    token = jwt.encode(
        payload.model_dump(),
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(loop_scope="function")
async def access_token_user() -> dict:
    return auth_header(["user"])


@pytest_asyncio.fixture(loop_scope="function")
async def access_token_admin() -> dict:
    return auth_header(["admin"])
