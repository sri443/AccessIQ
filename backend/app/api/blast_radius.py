from fastapi import APIRouter, HTTPException
from app.api.analysis import ANALYZED_USERS
from app.services.blast_radius_analyzer import BlastRadiusAnalyzer

router = APIRouter()


@router.get("/blast-radius/{user_id}")
async def get_blast_radius(user_id: str):
    """Calculate blast radius for a user"""
    if not ANALYZED_USERS:
        raise HTTPException(400, "Run analysis first")
    
    user = next((u for u in ANALYZED_USERS if u['id'] == user_id), None)
    if not user:
        raise HTTPException(404, "User not found")
    
    blast_radius = BlastRadiusAnalyzer.calculate_blast_radius(user)
    return blast_radius