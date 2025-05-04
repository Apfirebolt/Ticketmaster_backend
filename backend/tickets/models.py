from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, ForeignKey, Text, DateTime, Integer

from backend.db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, default=datetime.utcnow)
    location = Column(String(200), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
