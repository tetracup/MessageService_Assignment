from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    recipient = Column(String, index=True)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
"""
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, index=True)
    phone_number = Column(String, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    
    """
