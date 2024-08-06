from redis.asyncio import Redis
from utils.abstract import AsyncCacheStorage
from fastapi import Depends

redis: Redis | None = None


class RedisCacheAdapter(AsyncCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int):
        await self.redis.set(key, value, expire)


async def get_redis() -> Redis:
    return redis


async def get_cache(redis: Redis = Depends(get_redis)) -> AsyncCacheStorage:
    return RedisCacheAdapter(redis)
