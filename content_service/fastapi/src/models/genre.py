from pydantic import BaseModel


class Genre(BaseModel):
    uuid: str
    name: str


class GenreModel(Genre):
    class Config:
        populate_by_name = True
