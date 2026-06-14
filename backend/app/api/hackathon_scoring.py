from fastapi import APIRouter, HTTPException
from app.api.analysis import ANALYZED_USERS
from app.services.hackathon_metrics import HackathonMetrics

router = APIRouter()


@router.get("/hackathon-metrics")
async def get_hackathon_metrics():
    """Get all hackathon scoring metrics"""
    if not ANALYZED_USERS:
        raise HTTPException(400, "Run analysis first")
    
    metrics = HackathonMetrics.calculate_all_metrics(ANALYZED_USERS)
    return metrics