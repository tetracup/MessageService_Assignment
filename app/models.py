from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    
    recipient_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)

    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

    # Relationships to User
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    address = Column(String, index=True)
    phone_number = Column(String, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    sent_messages = relationship("Message", back_populates="sender", foreign_keys='Message.sender_id', cascade="all, delete-orphan")
    received_messages = relationship("Message", back_populates="recipient", foreign_keys='Message.recipient_id', cascade="all, delete-orphan")

    
    
