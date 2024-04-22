
from datetime import datetime
import logging
import secrets
import string
from typing import Annotated, cast
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
from jose import JWTError, jwt
from pydantic import ValidationError
from core.config import InvalidUserException, settings
from models.user_model import User
from schemas.auth_schema import TokenPayload
from schemas.user_schema import UserAuth, UserOut
from services.user_services import UserServices
logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user (token : Annotated[str, Depends(oauth2_scheme)])->User:
    credention_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"}
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.ALGORITHM)

        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Expired",
                headers={"WWW-Authenticate":"Bearer"}
            )

        user_id = token_data.user_id

        if user_id is None:
            raise credention_error
        
        
    except (JWTError, ValidationError):
    # except Exception as e:
        raise credention_error
    
    user = await UserServices.get_user_by_id(user_id)

    return user


async def get_current_active_user(user: Annotated[User, Depends(get_current_user)]):
    if user.disabled == True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive User",
            headers={"WWW-Authenticate":"Bearer"}
        )
    
    return user



