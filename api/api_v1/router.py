from fastapi import APIRouter
from api.api_v1.handlers.user import user_router
from api.api_v1.handlers.todo import todo_router
from api.api_v1.handlers.google import google_router

from .auth.jwt import auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(google_router, prefix="/auth", tags=["Google Auth"])
router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(todo_router, prefix="/todo", tags=["Todos"])