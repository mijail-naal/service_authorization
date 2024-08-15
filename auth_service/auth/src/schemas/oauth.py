from enum import Enum
from pydantic import BaseModel


class OAuthProvider(Enum):
    GOOGLE: str = 'google'
    YANDEX: str = 'yandex'
    VK: str = 'vk'


class OAuthUser(BaseModel):
    sub: int
    email: str
    name: str
    picture: str
