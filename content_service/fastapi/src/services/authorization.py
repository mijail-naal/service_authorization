import http
import time

from jose import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings


def decode_token(token: str) -> dict | None:
    try:
        decode_token = jwt.decode(
            token, settings.auth_password, algorithms=settings.auth_algorithm
        )
        return  decode_token if decode_token['exp'] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                                detail='Invalid authorization code.')

        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED,
                                detail='Only Bearer token might be accepted')

        decode_token = self.parse_token(credentials.credentials)

        if not decode_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                                detail='Invallid or expired token.')

        return decode_token


    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_token(jwt_token)


security_jwt = JWTBearer()