from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from app.core.response import resp_200, resp_401
from app.db.db_session import get_db
import json

router = APIRouter()

@router.get("/compute")
async def get_portfolio(etf_list, db: Session = Depends(get_db)):

    return resp_200()