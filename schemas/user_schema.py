from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from typing import Optional


class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="user email")
    username: str = Field(..., min_length=5, max_length=20, description="username")
    password: str = Field(..., min_length=5, max_length=20, description="password")


    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "email":"abc@abc.com",
            "username":"Johny",
            "password":"abc123"
        }
    )


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserOut(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    disabled: Optional[bool] = Field(default=False)


