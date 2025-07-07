from fastapi import APIRouter
from app.api.api_v1.router import login, visualization, conversation, portfolio

router = APIRouter()
router.include_router(login.router, tags=['User login and register'])
router.include_router(visualization.router, tags=['Visualization'])
router.include_router(conversation.router, tags=['LLM Conversations'])
router.include_router(portfolio.router, tags=['Portfolio'])
