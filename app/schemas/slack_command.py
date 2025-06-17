from typing import Dict, Optional
from pydantic import BaseModel, Field

class SlackSlashCommandRequest(BaseModel):
    """
    Schema for incoming Slack slash command requests.
    Based on Slack API documentation: https://api.slack.com/interactivity/slash-commands
    """
    token: str = Field(..., description="Verification token from Slack")
    team_id: str = Field(..., description="ID of the team where the command was triggered")
    team_domain: str = Field(..., description="Domain of the team")
    channel_id: str = Field(..., description="ID of the channel where the command was triggered")
    channel_name: str = Field(..., description="Name of the channel where the command was triggered")
    user_id: str = Field(..., description="ID of the user who triggered the command")
    user_name: str = Field(..., description="Username of the user who triggered the command")
    command: str = Field(..., description="The slash command that was triggered")
    text: Optional[str] = Field(None, description="Text after the slash command")
    response_url: str = Field(..., description="URL to send delayed responses to")
    trigger_id: str = Field(..., description="Trigger ID for opening modals")

class SlackCommandResponse(BaseModel):
    """
    Schema for responses to Slack slash commands.
    """
    response_type: str = Field("ephemeral", description="'ephemeral' or 'in_channel'")
    text: str = Field(..., description="Main text of the response")
    blocks: Optional[list] = Field(None, description="Slack Block Kit blocks")

class SlackModalView(BaseModel):
    """
    Schema for opening a modal view in Slack.
    """
    trigger_id: str = Field(..., description="Trigger ID from the slash command")
    view: Dict = Field(..., description="Modal view payload") 