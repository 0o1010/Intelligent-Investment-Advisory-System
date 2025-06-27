from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from app.core.response import resp_200, resp_401
from app.db.db_session import get_db
from app.schemas.user import UserCreate, UserBase, UserResp, UserModify
from app.models.user import User
import json

router = APIRouter()


@router.get('/info', summary='User Info')
async def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        user_data = {
            **user.__dict__,
            "existing_financial_portfolio": json.loads(user.existing_financial_portfolio or "[]"),
            "investment_goals": json.loads(user.investment_goals or "[]"),
            "investment_preference_restrictions": json.loads(user.investment_preference_restrictions or "[]"),
        }
        user_data.pop("_sa_instance_state", None)
        return resp_200(data=user_data)
    return resp_401(message="User not found")


@router.post('/update', summary='Modify User')
async def update_user(user: UserModify, db: Session = Depends(get_db)):
    update_data = user.dict()
    for key in ["existing_financial_portfolio", "investment_goals", "investment_preference_restrictions"]:
        if isinstance(update_data[key], list):
            update_data[key] = json.dumps(update_data[key])
    db.query(User).filter(User.username == user.username).update(update_data)
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
    if db.query(User).filter(User.username == user.username).first():
        raise resp_401(message="Username already registered")
    db_user = User(
        username=user.username,
        password=user.password,
        age=user.age,
        family_status=user.family_status,
        annual_income_household=user.annual_income_household,
        annual_disposable_surplus=user.annual_disposable_surplus,
        total_assets=user.total_assets,
        existing_financial_portfolio=json.dumps(user.existing_financial_portfolio),
        liabilities=user.liabilities,
        emergency_fund=user.emergency_fund,
        investment_experience=user.investment_experience,
        investment_period=user.investment_period,
        investment_goals=json.dumps(user.investment_goals),
        risk_tolerance_attitude=user.risk_tolerance_attitude,
        expected_return_range=user.expected_return_range,
        max_drawdown_tolerance=user.max_drawdown_tolerance,
        investment_preference_restrictions=json.dumps(user.investment_preference_restrictions),
        liquidity_needs_short_term=user.liquidity_needs_short_term,
        financial_other=user.financial_other,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return resp_200(data=user.username)
