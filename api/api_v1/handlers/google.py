import os
from fastapi import APIRouter, Request, HTTPException, status, Form

from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi.responses import RedirectResponse

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from core.config import settings
from core.security import create_access_token, create_refresh_token

from services.google_services import google_user_service



google_router = APIRouter()



# To avoid error: Exception occurred: (insecure_transport) OAuth 2 MUST utilize https.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for testing, remove for production

# Load the secrets file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
REDIRECT_URI= os.environ.get("REDIRECT_URI")
FRONTEND_CLIENT_SUCCESS_URI= os.environ.get("FRONTEND_CLIENT_SUCCESS_URI")
FRONTEND_CLIENT_FAILURE_URI= os.environ.get("FRONTEND_CLIENT_FAILURE_URI")

@google_router.get("/google/login")
async def login(request: Request):
    flow = Flow.from_client_secrets_file(
         client_secrets_file=CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri = REDIRECT_URI
    )

    authorization_url, state =  flow.authorization_url(
        access_type = "offline",
        include_granted_scopes='true'
    )

    state.session["state"] = state

    return RedirectResponse(authorization_url)


@google_router.get('/google/callback')
async def auth(request: Request):
    
    try:
        state = request.session["state"]

        if not state or state != request.query_params.get('state'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State mismatch"
            )
        
        flow = Flow.from_client_secrets_file(
            client_secrets_file=CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )

        authorization_response = str(request.url)

        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials

        idinfo = id_token.verify_oauth2_token(
            credentials.id_token, 
            google_requests.Request(), 
            flow.client_config['client_id']
        )

        user_email = idinfo["email"]

        user_name = idinfo['name']

        google_user = await google_user_service(user_email,username=user_name)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
        access_token = create_access_token(data={"sub": google_user.id}, expires_delta=access_token_expires)

        # Generate refresh token (you might want to set a longer expiry for this)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_TIME)
        refresh_token = create_refresh_token(data={"sub": google_user.email}, expires_delta=refresh_token_expires)
                
        # return google_user
        response = RedirectResponse(url='http://localhost:3000/google/user')
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="token_type", value="bearer"  , httponly=True)
        response.set_cookie(key="expires_in", value=str(access_token_expires)  , httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return response
    except HTTPException as http_exception:
        # Log the exception for debugging
        print(f"HTTPException occurred: {http_exception.detail}")

        # Append a failure reason to the redirect URL
        failure_url = f"{FRONTEND_CLIENT_FAILURE_URI}?google_login_failed={http_exception.detail}"
        return RedirectResponse(url=failure_url)

    except Exception as exception:
        # Log the general exception for debugging
        print(f"Exception occurred: {exception}")

        # Append a generic failure message to the redirect URL
        failure_url = f"{FRONTEND_CLIENT_FAILURE_URI}?google_login_failed=error"
        return RedirectResponse(url=failure_url)