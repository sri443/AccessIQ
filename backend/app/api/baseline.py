from fastapi import APIRouter, HTTPException
from app.api.upload import state
from app.api.analysis import ANALYZED_USERS
from app.services.behavioral_baseline import BehavioralBaseline

router = APIRouter()
baseline_engine = None


@router.post("/baseline/build")
async def build_baseline():
    """Build behavioral baseline from events data"""
    global baseline_engine
    
    if state.EVENT_DATA is None:
        raise HTTPException(400, "Upload events data first")
    
    baseline_engine = BehavioralBaseline(state.EVENT_DATA)
    return {
        "status": "baseline_built",
        "roles_analyzed": len(baseline_engine.role_baselines) if baseline_engine.role_baselines else 0
    }


@router.get("/baseline/user/{user_id}")
async def get_user_baseline(user_id: str):
    """Get behavioral deviation for a user"""
    if baseline_engine is None:
        raise HTTPException(400, "Build baseline first - POST /api/baseline/build")
    
    if not ANALYZED_USERS:
        raise HTTPException(400, "Run analysis first")
    
    user = next((u for u in ANALYZED_USERS if u['id'] == user_id), None)
    if not user:
        raise HTTPException(404, "User not found")
    
    deviation = baseline_engine.calculate_deviation(user)
    return deviation