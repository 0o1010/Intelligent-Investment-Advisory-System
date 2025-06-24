from sqlalchemy import Column, Integer, String
from app.db.base_class import Base


class ETF(Base):
    __tablename__ = "etf"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, index=True)
    label = Column(String)
