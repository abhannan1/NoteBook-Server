from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core.config import settings
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession
from beanie import init_beanie
import logging
from models.todo_model import Todo
from models.user_model import User
logger = logging.getLogger(__name__)
from api.api_v1.router import router
from starlette.middleware.sessions import SessionMiddleware


@asynccontextmanager
async def lifespan(app:FastAPI):
    client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING) # type: ignore
    try:
        await init_beanie(
            database=client.Todolist, 
            document_models=[User, Todo]  
            )

        yield 

    except Exception as e:
        raise RuntimeError(f"Exception occurred during Beanie initialization")

    finally:
        client.close()


# app : FastAPI = FastAPI()
app  = FastAPI(lifespan=lifespan
                        ,title=settings.PROJECT_NAME, 
                        openapi_url=f"{settings.API_V1_STR}/openapi.json",
                        description="Backend for FARM app",
                        version="1.0.0",
                        docs_url="/",
                        # terms_of_service="https://caxgpt.vercel.app/terms/",
                        contact={
                            "name": "Abdul Hannan",
                            "url": "https://localhost:5000/contact/",
                            "email": "ab.hannan142@gmail.com",
                        },
                        # license_info={
                        #     "name": "Apache 2.0",
                        #     "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
                        # },
                        # servers=[
                        #     {
                        #         "url": "https://localhost:5000",
                        #         "description": "Local server"
                        #     },
                        # ],
                        )




ORIGINS = ["http://localhost:5000"
            "http://localhost.tiangolo.com",
            "https://localhost.tiangolo.com",
            "http://localhost",
            "http://localhost:5000",
            "http://localhost:8000",
            "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.BACKEND_CORS_ORIGINS,  # Replace with your allowed origins
    allow_origins = settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY)


@app.exception_handler(RuntimeError)
async def handle_database_errors(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Database error"},
    )

app.include_router(router, prefix=settings.API_V1_STR)

@app.get('/hi')
async def hello():
    return {"message":"This is the best app"}




if __name__== "__main__":
    # import asyncio
    # asyncio.run(main())
    uvicorn.run(
        "app:app",
        port=5000,
        reload=True,
        log_level="info",
        host="localhost"
    )
   


# app.add_event_handler("startup", startup()) 

    