from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import declarative_base

from app.models.base import BaseModel


class URL(BaseModel):
    """
    Core URLs Table:
    Stores short_code -> original_url mapping[cite: 189].
    short_code serves as the primary key and shard key[cite: 189].
    """
    __tablename__ = "urls"

    short_code = Column(String(8), primary_key=True, nullable=False)
    original_url = Column(Text, nullable=False)