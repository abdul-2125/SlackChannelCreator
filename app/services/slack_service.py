import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import logging
import json
import requests

load_dotenv()
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')

client = WebClient(token=SLACK_BOT_TOKEN)
logger = logging.getLogger(__name__)

def create_channel(name: str, is_private: bool = False):
    try:
        response = client.conversations_create(
            name=name,
            is_private=is_private
        )
        return response['channel']['id']
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")

def lookup_user(email: str):
    try:
        resp = client.users_lookupByEmail(email=email)
        return resp['user']['id']
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")

def invite_users(channel: str, user_ids: list[str]):
    try:
        client.conversations_invite(channel=channel, users=','.join(user_ids))
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")

def token_info() -> dict:
    """Return basic information about the Slack token using auth.test."""
    try:
        resp = client.auth_test()
        return {
            "user_id": resp.get("user_id"),
            "team": resp.get("team"),
            "url": resp.get("url"),
        }
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")

def open_channel_creation_modal(trigger_id: str):
    """Open a modal dialog for channel creation."""
    try:
        modal_view = {
            "type": "modal",
            "callback_id": "channel_creation_modal",
            "title": {"type": "plain_text", "text": "Create Channel"},
            "submit": {"type": "plain_text", "text": "Create"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "channel_name_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "channel_name_input",
                        "placeholder": {"type": "plain_text", "text": "e.g. project-name"}
                    },
                    "label": {"type": "plain_text", "text": "Channel Name"}
                },
                {
                    "type": "input",
                    "block_id": "channel_type_block",
                    "element": {
                        "type": "static_select",
                        "action_id": "channel_type_select",
                        "options": [
                            {"text": {"type": "plain_text", "text": "Public"}, "value": "Public"},
                            {"text": {"type": "plain_text", "text": "Private"}, "value": "Private"}
                        ],
                        "initial_option": {"text": {"type": "plain_text", "text": "Public"}, "value": "Public"}
                    },
                    "label": {"type": "plain_text", "text": "Channel Type"}
                },
                {
                    "type": "input",
                    "block_id": "users_block",
                    "optional": True,
                    "element": {
                        "type": "multi_users_select",
                        "action_id": "users_select",
                        "placeholder": {"type": "plain_text", "text": "Select users to add"}
                    },
                    "label": {"type": "plain_text", "text": "Users to Add (Optional)"}
                }
            ]
        }
        
        response = client.views_open(trigger_id=trigger_id, view=modal_view)
        return response
    except SlackApiError as e:
        logger.error(f"Error opening modal: {e}")
        raise RuntimeError(f"Slack API error: {e.response['error']}")

def send_delayed_response(response_url: str, message: str, response_type: str = "ephemeral", blocks: list = None):
    """Send a delayed response to a slash command."""
    payload = {
        "text": message,
        "response_type": response_type
    }
    
    if blocks:
        payload["blocks"] = blocks
        
    try:
        response = requests.post(
            response_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending delayed response: {e}")
        return False
