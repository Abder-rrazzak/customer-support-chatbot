from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    intent = Column(String(100))
    confidence = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)