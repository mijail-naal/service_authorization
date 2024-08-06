from pydantic import BaseModel
from fastapi import Query

import core.config as config


class PaginatedParams(BaseModel):
    page: int = Query(
        default=1,
        ge=1,
        alias=config.PAGE_ALIAS,
        description=config.PAGE_DESC
    )
    size: int = Query(
        default=10,
        ge=1,
        le=config.MAX_PAGE_SIZE,
        alias=config.SIZE_ALIAS,
        description=config.SIZE_DESC
    )
