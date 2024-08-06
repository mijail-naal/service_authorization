from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from redis.asyncio import Redis

from db.redis import get_redis
from models.entity import User, Role
from schemas.role import RoleInDB, RoleCreate


class RoleService:
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
        
    async def create_role(self, role_create: RoleCreate, db: AsyncSession) -> RoleInDB | None:
        user_dto = jsonable_encoder(role_create)
        user = Role(**user_dto)
        res = await self._add_to_db(user, db)
        return res
    
    async def role_validation(self, role: str, db: AsyncSession) -> int | None:
        query = await db.execute(select(Role).where(Role.role == role))
        role = query.scalars().first()
        return role.id
    
    async def add_role(self, user: User, role_id: int, db: AsyncSession):
        user.role_id = role_id
        user = await self._add_to_db(user, db)
        return user
    
    async def revoke_role(self, user: User, db: AsyncSession):
        user.role_id = 1
        user = await self._add_to_db(user, db)
        return user
    
    async def delete_role(self, role_id: int, db: AsyncSession) -> None:
        query = delete(Role).where(Role.id == role_id)
        query.execution_options(synchronize_session="fetch")
        await db.execute(query)
        await db.commit()

    async def get_all_roles(self, db: AsyncSession) -> list[RoleInDB]:
        query = await db.execute(select(Role))
        roles = query.scalars().all()
        return roles



lru_cache()
def get_role_service(
        cache: Redis = Depends(get_redis)
) -> RoleService:
    return RoleService(cache)
