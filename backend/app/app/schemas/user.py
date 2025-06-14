from pydantic import BaseModel, EmailStr


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
        orm_mode = True


class UserResp(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
