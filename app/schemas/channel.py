from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel

class ChannelRequestCreate(BaseModel):
    channel_name: str
    requester_email: str
    requester_name: Optional[str] = None
    visibility: Literal['public', 'private']
    users_to_add: Optional[List[str]] = None
    form_submission_id: Optional[str] = None

class ChannelRequestResponse(BaseModel):
    id: int
    channel_name: str
    channel_id: Optional[str]
    status: Literal['pending', 'created', 'failed']
    created_at: datetime

    class Config:
        orm_mode = True


class CreateChannelRequest(BaseModel):
    channel_name: str
    channel_type: Literal['Public', 'Private']
    who_for: Optional[str] = None
    submitted_by: Optional[str] = None


class CreateChannelResponse(BaseModel):
    channel_name: str
    channel_id: str


class TokenInfoResponse(BaseModel):
    user_id: str
    team: Optional[str] = None
    url: Optional[str] = None
