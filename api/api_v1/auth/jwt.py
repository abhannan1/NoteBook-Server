from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.config import settings
from core.security import create_access_token, create_refresh_token, token_service
from deps.user_deps import get_current_active_user, get_current_user
from models.user_model import User
from schemas.auth_schema import TokenSchema
from schemas.user_schema import UserAuth
from services.user_services import UserServices

auth_router = APIRouter()


@auth_router.post("/login", summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login_user(form_data : Annotated[UserAuth, Depends(OAuth2PasswordRequestForm)]):
    user = await UserServices.authenticate_user(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
    access_token = create_access_token(subject={"user_id": user.user_id}, expire_delta=access_token_expires)

    refresh_token = create_refresh_token(subject={"email":user.email})

    return {
        "access_token":access_token,
        "token_type":"Bearer",
        "expires_in": access_token_expires,
        "refresh_token":refresh_token
    }

@auth_router.get("/test-token", summary="Test if the access token is valid", response_model=User)
async def test_token(user: Annotated[User, Depends(get_current_active_user)]):
    return user


@auth_router.post("/token", summary="Token URl For OAuth Code Grant Flow", response_model=TokenSchema)
async def token_manager(
    grant_type: str = Form(...),
    refresh_token: Optional[str] = Form(None),
):
    """
    Token URl For OAuth Code Grant Flow

    Args:
        grant_type (str): Grant Type
        refresh_token (Optional[str], optional)

    Returns:
        access_token (str)
        token_type (str)
        expires_in (int)
        refresh_token (str)
    """
    return await token_service(grant_type, refresh_token)