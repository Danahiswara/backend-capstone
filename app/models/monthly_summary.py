from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class MonthlySummary(Base):
    __tablename__ = "monthly_summary"

    summary_id = Column(Integer, primary_key=True, index=True)

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    type_id = Column(Integer, ForeignKey("types.type_id"))

    total_incoming = Column(Integer, default=0)
    total_outgoing = Column(Integer, default=0)

    # relationship
    type = relationship("Type")