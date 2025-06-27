from sqlalchemy import Column, Integer, String
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    age = Column(Integer, default=0)
    family_status = Column(Integer, default=0)
    annual_income_household = Column(Integer, default=0)
    annual_disposable_surplus = Column(Integer, default=0)
    total_assets = Column(Integer, default=0)
    existing_financial_portfolio = Column(String, default="")
    liabilities = Column(Integer, default=0)
    emergency_fund = Column(Integer, default=0)
    investment_experience = Column(Integer, default=0)
    investment_period = Column(Integer, default=0)
    investment_goals = Column(String, default="")
    risk_tolerance_attitude = Column(Integer, default=0)
    expected_return_range = Column(Integer, default=0)
    max_drawdown_tolerance = Column(Integer, default=0)
    investment_preference_restrictions = Column(String, default="")
    liquidity_needs_short_term = Column(Integer, default=0)
    financial_other = Column(String, default="")

