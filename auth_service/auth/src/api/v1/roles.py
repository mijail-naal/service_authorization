from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

from db.postgres import get_session
from services.user import UserService, get_user_service
from services.role import RoleService, get_role_service
from schemas.user import UserAccess, UserRoles
from schemas.role import (
    RoleInDB, 
    RoleCreate,
    AsignRole,
    RoleDelete
)
from .user_auth import roles_required, AuthRequest, UserInDBRole


router = APIRouter()
auth_dep = AuthJWTBearer()


@router.get('/', response_model=list[RoleInDB], status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def get_roles(
    request: AuthRequest,
    role_service: RoleService = Depends(get_role_service), 
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> RoleInDB:
    await authorize.jwt_required()

    return await role_service.get_all_roles(db)


@router.post('/create', response_model=RoleInDB, status_code=HTTPStatus.CREATED)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def create_role(
    request: AuthRequest,
    role_create: RoleCreate,
    role_service: RoleService = Depends(get_role_service), 
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> RoleInDB:
    #await authorize.jwt_required()

    return await role_service.create_role(role_create, db)


@router.post('/asign', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def asign_role(
    request: AuthRequest,
    data: AsignRole,
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service), 
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    role_id = await role_service.role_validation(data.role, db)
    if user.role_id == role_id:
        return {"detail": "Already have this role"}
    await role_service.add_role(user, role_id, db)
    return {"detail": "Role successfully added"}


@router.patch('/revoke', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def revoke_role(
    request: AuthRequest,
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service), 
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    if user.role_id == 1:
        return {"detail": "Can not revoke this role"}
    await role_service.revoke_role(user, db)
    return {"detail": "Role successfully revoked"}


@router.delete('/delete', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def delete_role(
    request: AuthRequest,
    data: RoleDelete,
    role_service: RoleService = Depends(get_role_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
):
    await authorize.jwt_required()

    role_id = await role_service.role_validation(data.role, db)
    print(role_id)
    await role_service.delete_role(role_id, db)
    return {"detail": "Role successfully deleted"}
