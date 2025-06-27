from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class UserModify(BaseModel):
    username: str
    age: int
    family_status: int
    annual_income_household: int
    annual_disposable_surplus: int
    total_assets: int
    existing_financial_portfolio: List[str]
    liabilities: int
    emergency_fund: int
    investment_experience: int
    investment_period: int
    investment_goals: List[str]
    risk_tolerance_attitude: int
    expected_return_range: int
    max_drawdown_tolerance: int
    investment_preference_restrictions: List[str]
    liquidity_needs_short_term: int
    financial_other: Optional[str] = ""

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    age: int
    family_status: int
    annual_income_household: int
    annual_disposable_surplus: int
    total_assets: int
    existing_financial_portfolio: List[str]
    liabilities: int
    emergency_fund: int
    investment_experience: int
    investment_period: int
    investment_goals: List[str]
    risk_tolerance_attitude: int
    expected_return_range: int
    max_drawdown_tolerance: int
    investment_preference_restrictions: List[str]
    liquidity_needs_short_term: int
    financial_other: Optional[str] = ""

    class Config:
        from_attributes = True


class UserResp(UserBase):
    id: int

    class Config:
        from_attributes = True

