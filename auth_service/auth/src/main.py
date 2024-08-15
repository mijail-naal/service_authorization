import logging
import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.middleware.sessions import SessionMiddleware

from api.v1 import users, roles, admin, oauth
from api.v1.user_auth import get_current_user_global
from core.config import settings
from core.logger import LOGGING
from db import redis
from utils.tracer import configure_tracer


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True)
    if settings.debug:
        from db.postgres import create_database
        await create_database()
    await FastAPILimiter.init(redis.redis)
    yield
    await redis.redis.close()
    await FastAPILimiter.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['roles'], dependencies=[Depends(get_current_user_global)])
app.include_router(admin.router, prefix='/api/v1/admin', tags=['admin'], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
app.include_router(oauth.router, prefix='/api/v1/oauth', tags=['oauth'], dependencies=[Depends(RateLimiter(times=2, seconds=5))])


# OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Tracer
@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return  response


if settings.enable_tracer:
    configure_tracer()

FastAPIInstrumentor.instrument_app(app)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
