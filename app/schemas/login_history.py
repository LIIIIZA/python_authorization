from datetime import datetime
from pydantic import BaseModel, IPvAnyAddress
from typing import Optional

class LoginHistoryBase(BaseModel):
    auth_method: str
    ip_address: Optional[IPvAnyAddress] = None
    user_agent: Optional[str] = None

class LoginHistoryResponse(LoginHistoryBase):
    id: str
    user_id: str
    timestamp: datetime

    class Config:
        orm_mode = True
