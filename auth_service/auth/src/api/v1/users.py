from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

from db.postgres import get_session
from db.redis import redis
from services.user import UserService, get_user_service
from schemas.user import (
    UserInDB, 
    UserCreate, 
    UsernameLogin, 
    JTWSettings, 
    UserAccess, 
    ChangeUsername, 
    ChangePassword, 
    UserHistoryInDB,
    UserRoles
)
from models.abstract import PaginatedParams
from .user_auth import roles_required, UserInDBRole, AuthRequest


router = APIRouter()
auth_dep = AuthJWTBearer()
jtw_settings = JTWSettings()


@AuthJWT.load_config
def get_config():
    return jtw_settings


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    entry = await redis.get(jti)
    return entry and entry == True


@router.post('/signup', response_model=UserInDB, status_code=HTTPStatus.CREATED)
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service), 
    db: AsyncSession = Depends(get_session),
):
    return await user_service.create_user(user_create, db)


@router.post('/signin', response_model=UserAccess, status_code=HTTPStatus.OK)
async def login(
    credentials: UsernameLogin,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> UserAccess | None:
    user = await user_service.user_validation(credentials, db)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Username doesn\'t exists'
        )
    if not user.check_password(credentials.password):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Incorrect password'
        )
    tokens = await user_service.create_user_tokens(credentials, authorize)
    await authorize.set_access_cookies(tokens.access_token)
    await authorize.set_refresh_cookies(tokens.refresh_token)
    await user_service.add_login_to_history(user, db)
    return tokens


@router.post('/signout', status_code=HTTPStatus.OK)
async def logout(
    user_service: UserService = Depends(get_user_service),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()
    #await user_service.revoke_tokens(tokens, authorize, jtw_settings)
    await authorize.unset_jwt_cookies()
    return {"detail": "Logged out successfully"}


@router.post('/refresh', status_code=HTTPStatus.OK)
async def refresh(
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_refresh_token_required()

    current_user = await authorize.get_jwt_subject()
    new_access_token = await authorize.create_access_token(subject=current_user)
    await authorize.set_access_cookies(new_access_token)
    return {"access_token": new_access_token}


@router.patch('/change-username', status_code=HTTPStatus.OK)
async def change_username(
    login: ChangeUsername,
    user_service: UserService = Depends(get_user_service), 
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    await user_service.change_login(login, user, db)
    await authorize.unset_jwt_cookies()
    return {"detail": "Username successfully updated"}
    

@router.patch('/change-password', status_code=HTTPStatus.OK)
async def change_password(
    login: ChangePassword,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    print('password',user)
    await user_service.change_password(login, user, db)
    await authorize.unset_jwt_cookies()
    return {"detail": "Password successfully updated"}


@router.get(
        '/login-history',
        response_model=list[UserHistoryInDB],
        status_code=HTTPStatus.OK)
async def login_history(
    pagination: PaginatedParams = Depends(),
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> list[UserHistoryInDB]:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    history = await user_service.get_login_history(user, pagination.page, pagination.size, db)
    login_history = [UserHistoryInDB(
        id=i.id, user_id=i.user_id, logged_at=i.logged_at
    ) for i in history]
    return login_history


@router.get('/users', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def get_users(
    *,
    request: AuthRequest,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> list[UserInDBRole]:
    await authorize.jwt_required()

    return await user_service.get_all_users(db)
