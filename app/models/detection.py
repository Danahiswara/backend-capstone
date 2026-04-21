from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Detection(Base):
    __tablename__ = "detections"

    detection_id = Column(Integer, primary_key=True, index=True)

    item_id = Column(Integer, ForeignKey("items.item_id"))
    type_id = Column(Integer, ForeignKey("types.type_id"))
    object_count = Column(Integer, nullable=False)
    mask_path = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)

    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    item = relationship("Item", back_populates="detection")
    type = relationship("Type", back_populates="detection")
