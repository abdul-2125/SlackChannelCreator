import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

client = WebClient(token=SLACK_BOT_TOKEN)

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
