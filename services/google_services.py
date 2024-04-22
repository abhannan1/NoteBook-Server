import secrets
import string
from fastapi import status
from core.config import InvalidUserException
from models.user_model import User
from schemas.user_schema import UserAuth, UserOut
from services.user_services import UserServices


async def google_user_service(user_email:str, username:str)->User:
    """
    Service function to sign up/login users.

    Args:
        user_email: The user_email.
        db (Session): The database session.

    Returns:
        The user data.
    """
    try:
        user = await UserServices.get_user_by_email(user_email)

        if user is None:

            password_length = 12
            characters = string.ascii_letters + string.digits + string.punctuation
            random_password = ''.join(secrets.choice(characters) for i in range(password_length))

            user_data = UserAuth(
                username=username,
                email=user_email,
                password=random_password
            )

            new_user = await UserServices.create_user(user_data)

            return new_user
        
        return new_user
    

    except InvalidUserException as e:
        # Re-raise the exception to be handled in the web layer
        raise InvalidUserException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        # Re-raise general exceptions to be handled in the web layer
        raise e
