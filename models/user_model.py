from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import Annotated, Optional
from uuid import UUID, uuid4
import datetime

import pymongo
# from bson import datetime


class User(Document):
    user_id: Annotated[UUID, Field(default_factory=uuid4, unique=True, primary_key=True)]
    username: Annotated[str, Indexed(unique=True)]
    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str
    first_name: Optional[str] = None 
    last_name: Optional[str] = None
    disabled: Optional[bool] = Field(default=False)


    def __repr__(self) -> EmailStr:
        return f"<User {self.email}"
    
    def __str__(self) -> EmailStr:
        return self.email
    
    def __hash__(self) -> int:
        return hash(self.email)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.email == other.email
        return False
    
    @property 
    def create(self) -> datetime:
        return self.user_id.generation_time
    
    @classmethod
    async def by_email(cls,email:str):
        return await cls.find_one(cls.email == email)
    
    class Settings:
        name = "user"
        indexes = [
            [
                ("email", pymongo.TEXT),
                ("username", pymongo.TEXT)
            ]
        ]
        bson_encoders = {

        }
        
    