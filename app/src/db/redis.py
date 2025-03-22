import json
from typing import Any

from redis.asyncio import Redis

redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


class RedisCache:
    def __init__(self, cache_client):
        self.cache_client = cache_client

    async def get_from_cache(self, key: str) -> dict | None:
        data = await self.cache_client.get(key)
        if data:
            return json.loads(data)
        return None

    async def put_to_cache(self, key: str, value: Any, ttl: int) -> None:
        await self.cache_client.set(key, json.dumps(value), ex=ttl)
