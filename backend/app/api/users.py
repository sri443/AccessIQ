from fastapi import APIRouter, HTTPException
from app.api.analysis import ANALYZED_USERS
from app.models.schemas import UserDetail

router = APIRouter()

@router.get("/{user_id}")
async def get_user_detail(user_id: str) -> UserDetail:
    if not ANALYZED_USERS: raise HTTPException(400, "Please run analysis first")
    user = next((u for u in ANALYZED_USERS if u['id'] == user_id), None)
    if not user: raise HTTPException(404, "User not found")
    
    # Safely extract compliance mapping names
    violations = [f['type'] for f in user['findings']]
    return UserDetail(**user, compliance_violations=violations)