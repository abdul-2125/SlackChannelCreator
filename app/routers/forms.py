from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.channel import ChannelRequestCreate, ChannelRequestResponse
from app.models.channel_request import ChannelRequest
from app.services.slack_service import create_channel, lookup_user, invite_users
import logging

router = APIRouter(prefix="/forms", tags=["forms"])
logger = logging.getLogger(__name__)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/webhook", response_model=ChannelRequestResponse)
async def forms_webhook(payload: ChannelRequestCreate, db: Session = Depends(get_db)):
    # Store request in DB
    req = ChannelRequest(
        channel_name=payload.channel_name,
        requester_email=payload.requester_email,
        requester_name=payload.requester_name,
        visibility=payload.visibility,
        users_to_add=payload.users_to_add,
        form_submission_id=payload.form_submission_id,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    logger.info("Stored channel request %s", req.id)

    # Channel creation workflow
    try:
        channel_id = create_channel(req.channel_name, req.visibility == 'private')
        req.channel_id = channel_id
        req.status = 'created'
        if req.users_to_add:
            user_ids = []
            for email in req.users_to_add:
                user_ids.append(lookup_user(email))
            invite_users(channel_id, user_ids)
    except Exception as e:
        req.status = 'failed'
        req.error_message = str(e)
        db.commit()
        logger.error("Channel creation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    db.commit()
    return req
