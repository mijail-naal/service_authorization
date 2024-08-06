from fastapi import Depends, HTTPException
from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session

from models.user import User

from services.user import UserService, get_user_service


async def superuser_required(
    authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    await authorize.jwt_required()
    user = await user_service.get_user(db, authorize)
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Access forbidden: superuser privileges required")
    return user
