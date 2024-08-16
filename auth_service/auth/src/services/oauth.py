from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from redis.asyncio import Redis

from db.redis import get_redis
from models.entity import Provider
from schemas.oauth import CreateProvider, ProviderInDB


class OAuthService:
    def __init__(self, cache: Redis) -> None:
        self.cache = cache

    async def _add_to_db(self, obj, db: AsyncSession) -> object | None:
        try:
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj
        except IntegrityError as e:
            msg = str(e.orig).split("\n")[1][9:]
            raise HTTPException(status_code=HTTPStatus.FOUND, detail=msg)

    async def provider_validation(self, name: str, db: AsyncSession) -> int | None:
        query = await db.execute(select(Provider).where(Provider.name == name))
        provider = query.scalars().first()
        return provider.id

    async def create_provider(self, role_create: CreateProvider, db: AsyncSession) -> ProviderInDB | None:
        user_dto = jsonable_encoder(role_create)
        user = Provider(**user_dto)
        res = await self._add_to_db(user, db)
        return res

    async def delete_provider(self, provider_id: int, db: AsyncSession) -> None:
        query = delete(Provider).where(Provider.id == provider_id)
        query.execution_options(synchronize_session="fetch")
        await db.execute(query)
        await db.commit()


@lru_cache()
def get_oauth_service(
        cache: Redis = Depends(get_redis)
) -> OAuthService:
    return OAuthService(cache)
