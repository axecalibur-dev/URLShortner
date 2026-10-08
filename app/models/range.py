from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import declarative_base

from app.models.base import BaseModel


class Range(BaseModel):
    """
    Ticket Server Table:
    Holds partitioned ranges so the API service can grab
    atomic, collision-free numbers without a single global counter bottleneck[cite: 192, 193].
    """
    __tablename__ = "ranges"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    start_id = Column(BigInteger, nullable=False)
    end_id = Column(BigInteger, nullable=False)
    current_id = Column(BigInteger, nullable=False)
    is_exhausted = Column(Boolean, default=False, nullable=False)