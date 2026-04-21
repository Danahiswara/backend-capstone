from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class OutgoingLog(Base):
    __tablename__ = "outgoing_log"

    outgoing_id = Column(Integer, primary_key=True, index=True)

    type_id = Column(Integer, ForeignKey("types.type_id"))
    quantity = Column(Integer, nullable=False)
    method = Column(String)
    detection_id = Column(Integer, ForeignKey("detections.detection_id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    type = relationship("Type", back_populates="outgoing_log")
    user = relationship("User", back_populates="outgoing_log")
    detection = relationship("Detection", lazy="joined")
