from fastapi import FastAPI
import logging
from app.config import settings
from app.api.api_v1.api import router
from starlette.middleware.cors import CORSMiddleware
from app.db.db_session import engine
import app.models as models

def register_databse(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)

def register_router(app: FastAPI):
    app.include_router(
        router
    )


def register_cors(app: FastAPI):
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def create_app():
    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.PROJECT_NAME,
        # swagger_ui_parameters={"operationsSorter": "method"}
    )
    register_databse(app)
    register_router(app)
    register_cors(app)
    return app
