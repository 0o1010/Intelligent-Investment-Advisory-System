from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from app.core.response import resp_200, resp_401
from app.db.db_session import get_db
from app.schemas.user import UserCreate, UserBase, UserResp,UserModify
from app.models.user import User
import app.models as models

router = APIRouter()


@router.get('/info', summary='User Info')
async def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    return resp_200(data=UserCreate.from_orm(user).dict())

@router.post('/update', summary='Modify User')
async def update_user(user: UserModify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user.username).update(user.dict())
    db.commit()
    return resp_200()

@router.post('/login', summary='User Login')
async def login(user: UserBase, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user and db_user.password == user.password:
        message = 'Login Successfully'
        return resp_200(data=user.username, message=message)
    else:
        message = 'Incorrect username or password'
        return resp_401(message=message)


@router.post("/logout", summary='Logout')
def logout():
    return resp_200(data={'logout': True}, message='Logout successfully')


@router.post("/register", summary='User Register', response_model=UserResp)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise resp_401(message="Username already registered")
    db_user = User(
        username=user.username,
        password=user.password,
        financial_status=user.financial_status,
        assets_percentage=user.assets_percentage,
        annual_income=user.annual_income,
        investment_experience=user.investment_experience,
        investment_period=user.investment_period,
        investment_goal=user.investment_goal,
        investment_attitude=user.investment_attitude,
        investment_preference=user.investment_preference,
        risk_tolerance=user.risk_tolerance
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return resp_200(data=user.username)
