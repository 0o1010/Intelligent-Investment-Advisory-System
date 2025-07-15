from sqlalchemy import Column, Integer, String
from app.db.base_class import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    user_input = Column(String)
    output = Column(String)
    model = Column(String)
