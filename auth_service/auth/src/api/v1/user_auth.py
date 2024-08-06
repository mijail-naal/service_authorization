from functools import wraps
from http import HTTPStatus

from pydantic import BaseModel, EmailStr
from fastapi import Request, APIRouter, Depends, HTTPException
from models.entity import Role
from fastapi.security import HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession
from async_fastapi_jwt_auth import AuthJWT

from db.postgres import get_session
from services.user import UserService, get_user_service

from schemas.user import UserInDB, UserInDBRole, UserRoles
from schemas.auth_request import AuthRequest


def roles_required(roles_list: list[UserRoles]):
    def decorator(fuction):
        @wraps(fuction)
        async def wrapper(*args, **kwargs):
            user: UserInDBRole = kwargs.get('request').custom_user
            if not user or user.role_id not in roles_list:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN, detail='Forbidden. Only authorized user have access'
                )
            return await fuction(*args, **kwargs)
        return wrapper
    return decorator


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request,
                       user_service: UserService = Depends(get_user_service),
                       db: AsyncSession = Depends(get_session)) -> UserInDBRole | None:
        authorize = AuthJWT(req=request)
        await authorize.jwt_optional()
        user_id = await authorize.get_jwt_subject()
        if not user_id:
            return None
        user = await user_service.get_user(db, authorize)
        return UserInDBRole.from_orm(user)


async def get_current_user_global(request: AuthRequest, user: AsyncSession = Depends(JWTBearer())):
    request.custom_user = user
