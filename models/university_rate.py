from sqlalchemy import Column, DECIMAL, DateTime, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from models.base import Base
import uuid

class UniversityRating(Base):
    __tablename__ = "university_rate"
    
    ur_uuid = Column(UUID(as_uuid=True), nullable=False,
                    default=uuid.uuid4, primary_key=True)
    u_uuid = Column(UUID(as_uuid=True), default=None)
    a_uuid = Column(UUID(as_uuid=True), default=None)
    rating = Column(DECIMAL(2, 1), nullable=False)
    rate_date = Column(DateTime, default=datetime.now())
    
    __table_args__ = (ForeignKeyConstraint(
        ["u_uuid", "a_uuid"], ["university.u_uuid", "account.a_uuid"]
    ),)