from uuid import UUID
from fastapi import Form, HTTPException,status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from pydantic import ValidationError
from core.config import settings
from schemas.auth_schema import TokenPayload, TokenSchema


# pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


pass_cxt = CryptContext(schemes="bcrypt", deprecated="auto")


def create_access_token(subject:Union[dict, Any],  expire_delta: timedelta | None = None):
    to_encode = subject.copy()

    # Convert UUID to string if it's present in the data
    if 'user_id' in to_encode and isinstance(to_encode.get('user_id'), UUID):
        to_encode['user_id'] = str(to_encode['user_id'])

    if expire_delta:
        expire_delta = datetime.now(timezone.utc) + expire_delta
    else:
        expire_delta = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)    
    
    to_encode.update({"exp": expire_delta})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
    return token


def create_refresh_token(subject: Union[dict, Any],  expire_delta: Union[timedelta, datetime, None] = None):
    to_encode = subject.copy()

    if expire_delta:
        expire_delta = datetime.now(timezone.utc) + expire_delta
    else:
        expire_delta = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_TIME)

    to_encode.update({"exp": expire_delta})
    token = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def hash_password(password: str):
    return pass_cxt.hash(password)

def verify_password(password: str, hashed_password:str):
    return pass_cxt.verify(password, hashed_password)


async def validate_refresh_token(token:str):
    from services.user_services import UserServices

    credention_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"}
    )

    try:

        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, settings.ALGORITHM)
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login Again, Session Expired",
                headers={"WWW-Authenticate":"Bearer"}
            )

        email = token_data.email

        if email is None:
            raise credention_error
        
    # except (JWTError, ValidationError):
    except Exception as e:
        raise HTTPException(
            detail=f"{e}",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    user = await UserServices.get_user_by_email(email)

    return user

# include session in args if using sql / db: Session = Depends(get_db)
async def token_service(grant_type: str = Form(...), refresh_token: Optional[str] = Form(...) ):
    """
    Generates access and refresh tokens based on the provided grant type.
    """
    from services.user_services import UserServices


    if grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required for grant_type 'refresh_token'",
            )

        user = await validate_refresh_token(refresh_token)

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


    elif grant_type == "authorization_code":
        # Handle the authorization code grant type
        # This would involve validating the authorization code and possibly exchanging it for tokens
        # Example: user = await validate_authorization_code(db, authorization_code)
        pass  # Replace with actual logic

    else:
        # If an unsupported grant type is provided, raise an error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported grant type")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
    access_token = create_access_token(subject={"user_id": user.user_id}, expire_delta=access_token_expires)

    refresh_token = create_refresh_token(subject={"email":user.email})

    return TokenSchema(**{
        "access_token":access_token,
        "token_type":"Bearer",
        "expires_in": access_token_expires,
        "refresh_token":refresh_token
    })



