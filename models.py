from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_input = Column(Text)
    ai_response = Column(Text)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    max_token: int = 1024  # Valor por defecto
