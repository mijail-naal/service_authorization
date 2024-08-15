from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

from db.postgres import get_session
from services.user import UserService, get_user_service
from schemas.user import UserEmailLogin


router = APIRouter()
auth_dep = AuthJWTBearer()


@router.post('/signin', status_code=HTTPStatus.OK)
async def login(
    credentials: UserEmailLogin,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
):
    user = await user_service.user_email_validation(credentials, db)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Email doesn\'t exists'
        )
    if not user.check_password(credentials.password):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Incorrect password'
        )
    return user
