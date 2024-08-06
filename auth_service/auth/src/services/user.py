from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from async_fastapi_jwt_auth import AuthJWT

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from redis.asyncio import Redis
from werkzeug.security import generate_password_hash

from db.redis import get_redis
from models.entity import User, UserHistory
from schemas.user import (
    UserInDB, 
    UserCreate,
    UsernameLogin,
    UserAccess, 
    JTWSettings, 
    ChangeUsername, 
    ChangePassword, 
    LoginHistory
)


class UserService:
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

    async def create_user(self, user_create: UserCreate, db: AsyncSession) -> UserInDB | None:
        user_dto = jsonable_encoder(user_create)
        user = User(**user_dto)
        new_user = await self._add_to_db(user, db)
        return new_user
 
    async def user_validation(self, credentials: UsernameLogin, db: AsyncSession) -> User | None:
        query = await db.execute(select(User).where(User.login == credentials.username))
        user = query.scalars().first()
        return user
    
    async def create_user_tokens(self, credentials: UsernameLogin, authorize: AuthJWT) -> UserAccess:
        access_token = await authorize.create_access_token(subject=credentials.username)
        refresh_token = await authorize.create_refresh_token(subject=credentials.username)
        return UserAccess(access_token=access_token, refresh_token=refresh_token)
    
    async def revoke_tokens(self, tokens: UserAccess, authorize: AuthJWT, jtw_settings: JTWSettings):
        access_jti = (await authorize.get_raw_jwt(encoded_token=tokens.access_token))['jti']
        refresh_jti = (await authorize.get_raw_jwt(encoded_token=tokens.refresh_token))['jti']
        await self.cache.setex(access_jti, jtw_settings.refresh_expires, "true")
        await self.cache.setex(refresh_jti, jtw_settings.refresh_expires, "true")

    async def refresh_token(self, tokens: UserAccess, authorize: AuthJWT) -> dict:
        current_user = (await authorize.get_raw_jwt(encoded_token=tokens.refresh_token))['sub']
        new_access_token = await authorize.create_access_token(subject=current_user)
        return {"access_token": new_access_token}

    async def get_user(self, db: AsyncSession, authorize: AuthJWT) -> User | None:
        current_user = (await authorize.get_raw_jwt())['sub']
        db_user = await db.execute(select(User).where(User.login == current_user))
        return db_user.scalars().first()
    
    async def change_login(self, login: ChangeUsername, user: User, db: AsyncSession) -> User:
        user.login = login.new_username
        user = await self._add_to_db(user, db)
        return user
    
    async def change_password(self, login: ChangePassword, user: User, db: AsyncSession):
        user.password = generate_password_hash(login.new_password)
        user = await self._add_to_db(user, db)
        return user

    async def add_login_to_history(self, user: User, db: AsyncSession) -> User:
        login_history = LoginHistory(user_id=user.id)
        user_dto = jsonable_encoder(login_history)
        user = UserHistory(**user_dto)
        user_history = await self._add_to_db(user, db)
        return user_history
    
    async def get_login_history(self, user: User, page: int, size: int, db: AsyncSession):
        page = page - 1
        db_user = await db.execute(
            select(UserHistory).where(UserHistory.user_id == user.id).\
                order_by(UserHistory.logged_at).limit(size).offset(page*size)
        )
        return db_user.scalars().all()
    
    async def get_all_users(self, db: AsyncSession) -> list[UserInDB]:
        query = await db.execute(select(User))
        users = query.scalars().all()
        return users


lru_cache()
def get_user_service(
        cache: Redis = Depends(get_redis)
) -> UserService:
    return UserService(cache)
