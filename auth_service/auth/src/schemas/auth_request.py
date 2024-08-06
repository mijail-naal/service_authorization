from fastapi import Request
from schemas.user import UserInDBRole


class AuthRequest(Request):
    custom_user: UserInDBRole