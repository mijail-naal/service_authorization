import logging
import uvicorn

from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from core.logger import LOGGING
from db import elastic
from db import redis
from utils.tracer import configure_tracer


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f'{settings.elastic_protocol}://{settings.elastic_host}:{settings.elastic_port}'
        ]
    )
    await FastAPILimiter.init(redis.redis)
    yield
    await redis.redis.close()
    await elastic.es.close()
    await FastAPILimiter.close()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'],
                   dependencies=[Depends(RateLimiter(times=2, seconds=5))])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'],
                   dependencies=[Depends(RateLimiter(times=2, seconds=5))])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'],
                   dependencies=[Depends(RateLimiter(times=2, seconds=5))])


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return response


configure_tracer()
FastAPIInstrumentor.instrument_app(app)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
