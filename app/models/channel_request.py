from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, JSON
from datetime import datetime
from app.database import Base

class ChannelRequest(Base):
    __tablename__ = "channel_requests"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String, nullable=False)
    channel_id = Column(String, nullable=True)
    requester_email = Column(String, nullable=False)
    requester_name = Column(String, nullable=True)
    visibility = Column(Enum('public', 'private'), nullable=False)
    users_to_add = Column(JSON, nullable=True)
    status = Column(Enum('pending', 'created', 'failed'), default='pending')
    error_message = Column(Text, nullable=True)
    form_submission_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
