from enum import Enum
from pydantic import BaseModel


class OAuthProvider(Enum):
    AUTH: str = 'auth'
    YANDEX: str = 'yandex'
    GOOGLE: str = 'google'
    VK: str = 'vk'


class OAuthUser(BaseModel):
    sub: int | None = None
    email: str | None = None
    name: str = ''
    family_name: str = ''
    given_name: str = ''


class CreateProvider(BaseModel):
    name: str


class DeleteProvider(CreateProvider):
    pass


class ProviderInDB(BaseModel):
    id: int
    name: str


class AssignProvider(BaseModel):
    name: str = 'user'
