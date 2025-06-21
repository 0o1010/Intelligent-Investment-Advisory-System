from sqlalchemy import Column, Integer, String
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    # age = Column(Integer, default=0)

    financial_status = Column(Integer, default=0)
    assets_percentage = Column(Integer, default=0)
    annual_income = Column(Integer, default=0)
    investment_experience = Column(Integer, default=0)
    investment_period = Column(Integer, default=0)
    investment_goal = Column(Integer, default=0)
    investment_attitude = Column(Integer, default=0)
    investment_preference = Column(Integer, default=0)
    risk_tolerance = Column(Integer, default=0)
