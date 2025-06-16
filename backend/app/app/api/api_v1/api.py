from fastapi import APIRouter
from app.api.api_v1.router import login, visualization, conversation

router = APIRouter()
router.include_router(login.router, tags=['User login and register'])
router.include_router(visualization.router, tags=['Visualization'])
router.include_router(conversation.router, tags=['LLM Conversations'])
# router.include_router(visualization.router, tags=['展示数据相关'])
