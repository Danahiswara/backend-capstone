from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String)
    image_path = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.user_id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    user = relationship("User", back_populates="item")
    detection = relationship("Detection", back_populates="item")
