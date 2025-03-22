from typing import Any

import jwt
from core.config import settings


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.exceptions.InvalidTokenError:
        return None

    return payload
