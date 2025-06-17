from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class SlackUser(BaseModel):
    id: str
    username: Optional[str] = None
    name: Optional[str] = None
    team_id: Optional[str] = None

class SlackTeam(BaseModel):
    id: str
    domain: Optional[str] = None

class SlackAction(BaseModel):
    action_id: str
    block_id: str
    value: Optional[str] = None
    type: str
    action_ts: str
    selected_option: Optional[Dict] = None
    selected_user: Optional[str] = None
    selected_users: Optional[List[str]] = None

class SlackViewState(BaseModel):
    values: Dict[str, Dict[str, Any]]

class SlackView(BaseModel):
    id: str
    team_id: str
    callback_id: str
    state: SlackViewState
    hash: str
    title: Dict
    type: str
    submit: Optional[Dict] = None
    close: Optional[Dict] = None
    previous_view_id: Optional[str] = None

class SlackInteractionPayload(BaseModel):
    type: str
    user: SlackUser
    api_app_id: str
    token: str
    container: Optional[Dict] = None
    trigger_id: str
    team: SlackTeam
    enterprise: Optional[Dict] = None
    is_enterprise_install: Optional[bool] = None
    channel: Optional[Dict] = None
    message: Optional[Dict] = None
    view: Optional[SlackView] = None
    actions: Optional[List[SlackAction]] = None
    response_url: Optional[str] = None 