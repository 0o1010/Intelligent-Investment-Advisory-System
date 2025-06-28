from fastapi import FastAPI
import json
from app.config import settings
from app.api.api_v1.api import router
from starlette.middleware.cors import CORSMiddleware
from app.db.db_session import engine
import app.models as models
import csv
from sqlalchemy.orm import Session
from app.db.db_session import SessionLocal
from app.models.etf import ETF
from app.models.user import User
from app.models.conversation import Conversation

db_initialized = False


def register_database(app: FastAPI):
    global db_initialized
    if db_initialized:
        return
    db_initialized = True
    models.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    with open("app/db/init_data/etf_list.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not db.query(ETF).filter_by(value=row['value']).first():
                db.add(ETF(value=row['value'], label=row['label']))
    with open("app/db/init_data/users.json", 'r', encoding='utf-8') as f:
        users = json.load(f)
        for u in users:
            if not db.query(User).filter_by(username=u['username']).first():
                user = User(**u)
                db.add(user)
        db.commit()
    with open("app/db/init_data/conversations.json", 'r', encoding='utf-8') as f:
        conversations = json.load(f)
        for c in conversations:
            user = db.query(User).filter_by(username=c['username']).first()
            existing = db.query(Conversation).filter_by(id=c['id']).first()
            if not existing and user:
                db.add(Conversation(**c))
    db.commit()
    db.close()


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
    register_database(app)
    register_router(app)
    register_cors(app)
    return app
