from fastapi import APIRouter, HTTPException
from app.api.upload import state
from app.api.analysis import ANALYZED_USERS
from app.services.timeline_generator import TimelineGenerator

router = APIRouter()


@router.get("/timeline/{user_id}")
async def get_user_timeline(user_id: str):
    """Generate investigation timeline for a user"""
    if not ANALYZED_USERS:
        raise HTTPException(400, "Run analysis first")
    
    user = next((u for u in ANALYZED_USERS if u['id'] == user_id), None)
    if not user:
        raise HTTPException(404, "User not found")
    
    timeline = TimelineGenerator.generate_timeline(user, state.EVENT_DATA)
    return timeline