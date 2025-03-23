from datetime import datetime, timedelta

import jwt
from core.config import settings
from db.postgres import get_postgres_session
from db.redis import RedisCache, get_redis
from fastapi.params import Depends
from models import RefreshToken
from redis import Redis
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, postgres_session: AsyncSession, redis: Redis):
        self.postgres_session = postgres_session
        self.redis = RedisCache(redis)

    async def generate_access_token(self, user_id: str, user_roles: list[str]):
        valid_till = datetime.now() + timedelta(hours=settings.access_token_exp_hours)
        payload = {
            "user_id": user_id,
            "exp": int(valid_till.timestamp()),
            "roles": user_roles,
        }

        return jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

    async def generate_refresh_token(self, user_id: str):
        valid_till = datetime.now() + timedelta(days=settings.refresh_token_exp_days)

        payload = {
            "user_id": user_id,
            "exp": int(valid_till.timestamp()),
        }

        jwt_token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

        async with self.postgres_session() as session:
            refresh_token = RefreshToken(
                user_id=user_id,
                token=jwt_token,
                expires_at=valid_till,
            )
            session.add(refresh_token)
            await session.commit()

            return refresh_token.token

    async def is_refresh_token_valid(self, refresh_token: str) -> bool:
        async with self.postgres_session() as session:
            return await session.execute(
                select(
                    exists(RefreshToken).where(
                        RefreshToken.token == refresh_token,
                        RefreshToken.expires_at >= datetime.now(),
                    )
                )
            )

    async def invalidate_refresh_token(self, refresh_token: str):
        async with self.postgres_session() as session:
            await session.execute(
                delete(RefreshToken).where(RefreshToken.token == refresh_token)
            )
            await session.commit()

    async def invalidate_user_refresh_tokens(self, user_id: str, exclude_token: str):
        async with self.postgres_session() as session:
            await session.execute(
                delete(RefreshToken).where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.token != exclude_token,
                )
            )
            await session.commit()

    async def update_refresh_token(
        self,
        user_id: str,
        refresh_token: str,
        user_roles: list[str],
    ) -> tuple[str, str]:
        await self.invalidate_refresh_token(refresh_token)
        refresh_token_new = await self.generate_refresh_token(user_id)
        access_token = await self.generate_access_token(user_id, user_roles)

        return refresh_token_new, access_token

    async def invalidate_access_token(self, token: str) -> None:
        await self.redis.put_to_cache(
            key=token, value=True, ttl=settings.access_token_exp_hours * 3600
        )

    async def is_access_token_valid(self, token: str) -> bool:
        invalid_token = await self.redis.get_from_cache(key=token)
        return False if invalid_token else True


def get_auth_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
    redis: Redis = Depends(get_redis),
):
    return AuthService(postgres_session, redis)
