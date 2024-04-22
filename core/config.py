from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl,HttpUrl,AnyUrl
from typing import List, cast
from decouple import config



class Settings(BaseSettings):
    PROJECT_NAME : str = "TODOIST"
    API_V1_STR:str = "/api/v1"
    JWT_SECRET_KEY:str = config("JWT_SECRET_KEY", cast=str) 
    JWT_REFRESH_SECRET_KEY:str = config("JWT_REFRESH_SECRET_KEY", cast=str)
    SESSION_MIDDLEWARE_SECRET_KEY : str = config("SESSION_MIDDLEWARE_SECRET_KEY", cast=str)
    MONGO_CONNECTION_STRING : str = config("MONGO_CONNECTION_STRING", cast=str)
    ALGORITHM:str= "HS256"
    REFRESH_TOKEN_EXPIRE_TIME: int = 7 * 24 * 60
    ACCESS_TOKEN_EXPIRE_TIME: int = 10

    BACKEND_CORS_ORIGINS: List[str] =[
        config("BACKEND_CORS_ORIGIN1",cast=str),
        config("BACKEND_CORS_ORIGIN2",cast=str),
        config("BACKEND_CORS_ORIGIN3",cast=str)
        ]

    class Config:
        case_sensitive=True


settings = Settings()



class InvalidUserException(Exception):
    """
    Exception raised when a user is not found in the database or if the user data is invalid.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)