from sqlalchemy import Column, Integer, String, DateTime
# from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    is_approved = Column(String)

    # created_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationship
    item = relationship("Item", back_populates="user")
    incoming_log = relationship("IncomingLog", back_populates="user")
    outgoing_log = relationship("OutgoingLog", back_populates="user")
