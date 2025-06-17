from fastapi import APIRouter, HTTPException
from app.services.slack_service import create_channel, token_info
from app.schemas.channel import CreateChannelRequest, CreateChannelResponse, TokenInfoResponse
import logging

router = APIRouter(tags=["slack"])
logger = logging.getLogger(__name__)

@router.post("/create-channel", response_model=CreateChannelResponse)
async def create_channel_endpoint(payload: CreateChannelRequest):
    """Create a Slack channel directly via API."""
    is_private = payload.channel_type.lower() == "private"
    try:
        channel_id = create_channel(payload.channel_name, is_private)
        return CreateChannelResponse(channel_name=payload.channel_name, channel_id=channel_id)
    except Exception as e:
        logger.error("Channel creation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/token-info", response_model=TokenInfoResponse)
async def debug_token_info():
    """Return basic information about the configured Slack token."""
    try:
        info = token_info()
        return info
    except Exception as e:
        logger.error("Token info retrieval failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
