from fastapi import APIRouter, Depends, HTTPException, status
from deps.user_deps import get_current_active_user, get_current_user
from schemas.user_schema import UserAuth, UserOut, UserUpdate
from typing import Annotated, cast
from models.user_model import User
from core.security import pass_cxt
from services.user_services import UserServices
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from pymongo.errors import OperationFailure

user_router = APIRouter()

@user_router.post("/register", summary="Create new user", response_model=UserOut)
async def register_user(user: UserAuth):
    try:
        new_user = await UserServices.create_user(user)
    except (DuplicateKeyError, ValidationError, OperationFailure):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with this email or username already exists"
        )
    
    return new_user

@user_router.get("/me", summary="Get details of current user", response_model=UserOut)
async def get_user(user: Annotated[User, Depends(get_current_active_user)]):
    return user

@user_router.post("/update", response_model=UserOut)
async def update_user(data:UserUpdate, user: Annotated[User, Depends(get_current_active_user)]):
    try:
        user = await UserServices.update_user(user.id, data)
        return UserOut(**user)
    except OperationFailure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update Failed"
        )
    
