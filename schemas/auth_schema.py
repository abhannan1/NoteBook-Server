from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Union

class TokenSchema(BaseModel):
    access_token : str
    expires_in: timedelta
    token_type: str
    refresh_token : str


class TokenPayload(BaseModel):
    # sub : Union[UUID, str] = None
    user_id: UUID| None = None
    email: str| None = None
    exp : int | None = None
