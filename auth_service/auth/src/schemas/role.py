from pydantic import BaseModel


class RoleCreate(BaseModel):
    role: str


class RoleDelete(RoleCreate):
    pass


class RoleInDB(BaseModel):
    id: int
    role: str


class AsignRole(BaseModel):
    role: str = 'user'
