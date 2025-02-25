from enum import Enum
from pydantic import BaseModel, AnyHttpUrl

class OAuthProvider(str, Enum):
    YANDEX = "yandex"

class OAuthResponse(BaseModel):
    auth_url: AnyHttpUrl

class OAuthCallback(BaseModel):
    code: str
    state: str