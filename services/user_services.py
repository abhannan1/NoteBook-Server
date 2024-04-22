import logging
from typing import Optional
from uuid import UUID

from pymongo.errors import OperationFailure
from schemas.user_schema import UserAuth, UserOut, UserUpdate
from models.user_model import User
from fastapi import HTTPException, status
from core.security import verify_password, hash_password

# from fastapi.security import OAuth2PasswordBearer
# from typing import Annotated, Any


class UserServices:
    @staticmethod
    async def get_user_by_email(email: str)-> Optional[User]:
        user = await User.find_one(User.email == email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not Found",
                headers={"WWW-Authenticate":"Bearer"}
            )
        return user
    
    @staticmethod
    async def get_user_by_username(username: str)-> Optional[User]:
        user = await User.find_one(User.username == username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not Found",
                headers={"WWW-Authenticate":"Bearer"}
            )
        return user
    
    @staticmethod
    async def get_user_by_id(id: UUID)-> Optional[User]:
        user  = await User.find_one(User.user_id == id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not Found",
                headers={"WWW-Authenticate":"Bearer"}
            )        
        return user

    @staticmethod
    async def update_user(id: UUID, data: UserUpdate):
        user = await User.find_one(User.user_id == id)
        if not user:
            raise OperationFailure("User does not exist")
        
        await user.update(
            {"$set": data.model_dump(exclude_unset=True)}
        )

        return user

    @staticmethod
    async def create_user(user: UserAuth)-> UserOut:
        match = await User.find_one(User.email == user.email)
        if match :
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= 'This email already exists'
        )

        match = await User.find_one(User.username == user.username)
        if match:
                raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail= 'This username already exists'
            )
        
        new_user = User(
        username = user.username,
        email = user.email,
        hashed_password= hash_password(user.password)
    )
        try:
             await new_user.save()
        except Exception as e:
            logging.debug(e)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= f'Some error has occured'
            )
        return new_user
    
    @staticmethod
    async def authenticate_user(email:str, password:str) -> Optional[User]:
        user = await UserServices.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not registered"
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wrong password"
            )
        
        return user
    





