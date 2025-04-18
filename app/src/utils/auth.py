from http import HTTPStatus
from typing import Any, List

import jwt
from core.config import settings
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class AccessTokenPayload(BaseModel):
    user_id: str
    exp: int
    roles: List[str]


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.exceptions.InvalidTokenError:
        return None

    return payload


def get_user_id_from_token(access_token: str) -> str:
    payload = decode_token(access_token)

    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    user_id = payload["user_id"]

    return user_id


def check_user_access(auth_data: dict[str, Any], user_id: str):
    if "admin" not in auth_data["roles"] and user_id != auth_data["user_id"]:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)


def check_admin_access(auth_data: dict[str, Any]):
    if "admin" not in auth_data["roles"]:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
