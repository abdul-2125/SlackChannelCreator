from fastapi import APIRouter, HTTPException, Request, Form, Depends
from app.services.slack_service import create_channel, token_info, open_channel_creation_modal, send_delayed_response, client
from app.schemas.channel import CreateChannelRequest, CreateChannelResponse, TokenInfoResponse
from app.schemas.slack_command import SlackCommandResponse, SlackSlashCommandRequest
from app.schemas.slack_interaction import SlackInteractionPayload
import logging
from typing import Optional
import hmac
import hashlib
import time
import os
from dotenv import load_dotenv

load_dotenv()
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')

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

@router.get("/debug/test-modal")
async def test_modal_endpoint():
    """Debug endpoint to test modal opening."""
    try:
        # Generate a test trigger ID (this won't work with a fake trigger ID, but helps debug the code flow)
        test_trigger = "test_trigger_" + str(int(time.time()))
        logger.info(f"Debug endpoint: Testing with trigger ID: {test_trigger}")
        
        # Test token info first
        token_response = token_info()
        logger.info(f"Token info: {token_response}")
        
        # The following will fail with a fake trigger ID, but helps diagnose permission issues:
        try:
            open_channel_creation_modal(test_trigger)
        except Exception as modal_error:
            logger.info(f"Expected modal error (fake trigger ID): {str(modal_error)}")
        
        # Show token permissions
        auth_test = client.auth_test()
        token_scopes = client.apps_permissions_info()
        
        return {
            "token_info": token_response,
            "auth_test": auth_test,
            "bot_scopes": token_scopes.get("info", {}).get("scopes", []),
            "note": "Modal test will fail with fake trigger_id - this is expected. Check logs for more details."
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def verify_slack_signature(request: Request):
    """Verify that the request is coming from Slack."""
    if not SLACK_SIGNING_SECRET:
        logger.warning("SLACK_SIGNING_SECRET not set, skipping verification")
        return True
        
    # Get headers
    slack_signature = request.headers.get("X-Slack-Signature", "")
    slack_timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    
    # Check for replay attacks
    if abs(time.time() - int(slack_timestamp)) > 60 * 5:
        logger.warning("Timestamp too old, possible replay attack")
        return False
        
    # Create signature base string
    sig_basestring = f"v0:{slack_timestamp}:{request.body}"
    
    # Generate HMAC signature
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    if not hmac.compare_digest(my_signature, slack_signature):
        logger.warning("Signature verification failed")
        return False
        
    return True

@router.post("/slack/commands/create-channel", response_model=SlackCommandResponse)
async def slash_create_channel(
    token: str = Form(...),
    team_id: str = Form(...),
    team_domain: str = Form(...),
    channel_id: str = Form(...),
    channel_name: str = Form(...),
    user_id: str = Form(...),
    user_name: str = Form(...),
    command: str = Form(...),
    text: Optional[str] = Form(None),
    response_url: str = Form(...),
    trigger_id: str = Form(...),
    request: Request = None
):
    """Handle /create-channel slash command."""
    
    logger.info(f"Received slash command: {command} from {user_name}")
    logger.info(f"Request data - trigger_id: {trigger_id}, response_url: {response_url}")
    
    # Debug headers
    headers = dict(request.headers.items()) if request else {}
    logger.info(f"Request headers: {headers}")
    
    # Verify Slack signature (commented out for initial testing)
    # if not verify_slack_signature(request):
    #     logger.error("Slack signature verification failed")
    #     raise HTTPException(status_code=401, detail="Signature verification failed")
    
    try:
        # Log before opening the modal
        logger.info(f"Attempting to open modal with trigger_id: {trigger_id}")
        
        # Open a modal for channel creation
        modal_response = open_channel_creation_modal(trigger_id)
        logger.info(f"Modal open response: {modal_response}")
        
        return SlackCommandResponse(
            text="Opening channel creation form..."
        )
    except Exception as e:
        logger.error(f"Error handling slash command: {e}", exc_info=True)
        # Return a message that will be visible to the user
        return SlackCommandResponse(
            text=f"Error: {str(e)}"
        )

@router.post("/slack/interactions")
async def slack_interactions(request: Request):
    """Handle Slack interactive components like modals."""
    try:
        # Parse form data
        form_data = await request.form()
        payload = form_data.get("payload", "{}")
        
        # Parse JSON payload
        interaction = SlackInteractionPayload.parse_raw(payload)
        
        # Handle different types of interactions
        if interaction.type == "view_submission" and interaction.view.callback_id == "channel_creation_modal":
            return handle_channel_modal_submission(interaction)
            
        return {"text": "Received interaction"}
    except Exception as e:
        logger.error(f"Error handling interaction: {e}")
        return {"text": f"Error: {str(e)}"}

def handle_channel_modal_submission(interaction):
    """Handle submission of the channel creation modal."""
    try:
        # Extract values from the submitted view
        values = interaction.view.state.values
        
        channel_name = values["channel_name_block"]["channel_name_input"]["value"]
        channel_type = values["channel_type_block"]["channel_type_select"]["selected_option"]["value"]
        is_private = channel_type.lower() == "private"
        
        # Create the channel
        channel_id = create_channel(channel_name, is_private)
        
        # Get selected users
        selected_users = []
        if "users_block" in values and "users_select" in values["users_block"]:
            selected_users = values["users_block"]["users_select"].get("selected_users", [])
        
        # Invite users if any were selected
        if selected_users:
            invite_users(channel_id, selected_users)
        
        # Send a confirmation message
        user_id = interaction.user.id
        channel_url = f"https://slack.com/app_redirect?channel={channel_id}"
        
        send_delayed_response(
            interaction.response_url,
            f"Channel <{channel_url}|#{channel_name}> has been created successfully!",
            "ephemeral"
        )
        
        return {"response_action": "clear"}
    except Exception as e:
        logger.error(f"Error creating channel from modal: {e}")
        return {
            "response_action": "errors",
            "errors": {
                "channel_name_block": f"Error: {str(e)}"
            }
        }
