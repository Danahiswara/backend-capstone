from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Type(Base):
    __tablename__ = "types"

    type_id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String)
    total_items = Column(Integer, nullable=False)

    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # relatonship
    detection = relationship("Detection", back_populates="type")
    incoming_log = relationship("IncomingLog", back_populates="type")
    outgoing_log = relationship("OutgoingLog", back_populates="type")