from datetime import timedelta

from pydantic import BaseModel

from core.config import settings


class JTWSettings(BaseModel):
    authjwt_secret_key: str = settings.authjwt_key
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_token_expires: int = timedelta(minutes=2)
    authjwt_refresh_token_expires: int = timedelta(days=30)
    access_expires: int = timedelta(minutes=15)
    refresh_expires: int = timedelta(minutes=15)
