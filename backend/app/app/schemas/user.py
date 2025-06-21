from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class UserModify(BaseModel):
    username: str
    financial_status: int
    assets_percentage: int
    annual_income: int
    investment_experience: int
    investment_period: int
    investment_goal: int
    investment_attitude: int
    investment_preference: int
    risk_tolerance: int

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    # password: str
    financial_status: int
    assets_percentage: int
    annual_income: int
    investment_experience: int
    investment_period: int
    investment_goal: int
    investment_attitude: int
    investment_preference: int
    risk_tolerance: int

    class Config:
        from_attributes = True


class UserResp(UserBase):
    id: int

    class Config:
        from_attributes = True

