import orjson
from functools import lru_cache

from elasticsearch import NotFoundError
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from db.elastic import get_search_service
from db.redis import get_cache

from models.genre import GenreModel
from utils.es import build_body
from utils.abstract import AsyncCacheStorage, AsyncSearchService

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, cache: AsyncCacheStorage, search_service: AsyncSearchService):
        self.cache = cache
        self.search_service = search_service

    async def get_by_id(self, genre_id: str) -> GenreModel | None:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_search_service(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_search_service(self, genre_id: str) -> GenreModel | None:
        doc = await self.search_service.get(index='genres', id=genre_id)
        return GenreModel(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> GenreModel | None:
        data = await self.cache.get(genre_id)
        if not data:
            return None
        genre = GenreModel.model_validate_json(data)
        return genre

    async def _put_genre_to_cache(self, genre: GenreModel):
        await self.cache.set(genre.uuid, genre.model_dump_json(), GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def get_genres(self, size: int) -> list[GenreModel]:
        cache_key = 'genre:all'
        body = build_body(size=size)
        genres = await self._genres_from_cache(cache_key)
        if genres:
            return genres
        genres = await self._get_genres_from_search_service(body)
        if not genres:
            return []
        await self._put_genres_to_cache(genres, cache_key)
        return genres

    async def _get_genres_from_search_service(self, body) -> list[GenreModel] | None:
        response = await self.search_service.search(index='genres', body=body)
        genres = [GenreModel(**doc['_source']) for doc in response['hits']['hits']]
        return genres

    async def _genres_from_cache(self, cache_key: str) -> list[GenreModel] | None:
        genres: list[GenreModel] = await self.cache.get(cache_key)
        if not genres:
            return None
        return orjson.loads(genres)

    async def _put_genres_to_cache(self, genres: list[GenreModel], cache_key: str):
        await self.cache.set(
            cache_key,
            orjson.dumps(jsonable_encoder(genres)),
            GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
        cache: AsyncCacheStorage = Depends(get_cache),
        search_service: AsyncSearchService = Depends(get_search_service),
) -> GenreService:
    return GenreService(cache, search_service)
