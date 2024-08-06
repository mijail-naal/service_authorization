from elasticsearch import AsyncElasticsearch, BadRequestError, NotFoundError
from utils.abstract import AsyncSearchService
from fastapi import Depends

es: AsyncElasticsearch | None = None


class ElasticsearchAdapter(AsyncSearchService):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get(self, index: str, id: str, **kwargs):
        try:
            return await self.elastic.get(index=index, id=id, **kwargs)
        except (NotFoundError, BadRequestError):
            return None

    async def search(
                self,
                index: str,
                body: dict,
                **kwargs
            ):
        try:
            return await self.elastic.search(
                index=index, body=body,
                **kwargs
            )
        except (NotFoundError, BadRequestError):
            return None


async def get_elastic() -> AsyncElasticsearch:
    return es


async def get_search_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> AsyncSearchService:
    return ElasticsearchAdapter(elastic)
