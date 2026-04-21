from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class IncomingLog(Base):
    __tablename__ = "incoming_log"

    incoming_id = Column(Integer, primary_key=True, index=True)

    type_id = Column(Integer, ForeignKey("types.type_id"))
    quantity = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    type = relationship("Type", back_populates="incoming_log")
    user = relationship("User", back_populates="incoming_log")
