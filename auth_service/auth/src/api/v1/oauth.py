from http import HTTPStatus
from secrets import token_urlsafe

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token

from db.postgres import get_session
from core.config import gs
from services.user import UserService, get_user_service
from services.oauth import OAuthService, get_oauth_service
from schemas.user import UserEmailLogin, UserCreate, UserRoles
from schemas.oauth import OAuthProvider, OAuthUser, ProviderInDB, \
                          CreateProvider, DeleteProvider
from schemas.auth_request import AuthRequest
from api.v1.user_auth import roles_required


router = APIRouter()
auth_dep = AuthJWTBearer()
config = Config(environ=gs.model_dump())
oauth = OAuth(config)


SERVER_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=SERVER_URL,
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',
    }
)


@router.get('/login', response_model=None)
async def login(request: Request, provider: OAuthProvider):
    # http://localhost:8001/api/v1/oauth/login?provider=google
    if provider.value != 'google':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=f'{provider.value} provider not implemented yet.'
        )
    redirect_uri = request.url_for('callback_login', provider=provider.value)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/callback/{provider}', response_model=None)
async def callback_login(
    request: Request,
    provider: OAuthProvider,
    user_service: UserService = Depends(get_user_service),
    provider_service: OAuthService = Depends(get_oauth_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
):
    # http://localhost:8001/api/v1/oauth/callback/google
    try:
        user_response: OAuth2Token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user_info = user_response.get("userinfo")
    user_data = OAuthUser(**user_info)

    username = 'user-' + token_urlsafe(10)
    password = token_urlsafe(10)

    login = username[:15]
    if not user_data.email:
        user_data.email = username + '@temp-email.com'

    credentials = UserEmailLogin(email=user_data.email, password="")
    user = await user_service.user_email_validation(credentials, db)

    if not user:
        user_create = UserCreate(
            login=login,
            email=user_data.email,
            password=password,
            first_name=user_data.name,
            last_name="",
        )

        await user_service.create_user(user_create, db)
    provider_id = await provider_service.provider_validation(provider.value, db)
    tokens = await user_service.create_user_tokens_with_email(credentials, authorize)
    await authorize.set_access_cookies(tokens.access_token)
    await authorize.set_refresh_cookies(tokens.refresh_token)
    await user_service.add_login_to_history(user, provider_id, db)
    return {'tokens': tokens}


@router.post('/create', response_model=ProviderInDB, status_code=HTTPStatus.CREATED)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def create_provider(
    request: AuthRequest,
    provider_create: CreateProvider,
    provider_service: OAuthService = Depends(get_oauth_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> ProviderInDB:
    await authorize.jwt_required()

    return await provider_service.create_provider(provider_create, db)


@router.delete('/delete', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def delete_provider(
    request: AuthRequest,
    data: DeleteProvider,
    provider_service: OAuthService = Depends(get_oauth_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
):
    await authorize.jwt_required()

    provider_id = await provider_service.provider_validation(data.name, db)
    print(provider_id)
    await provider_service.delete_provider(provider_id, db)
    return {"detail": "Provider successfully deleted"}
