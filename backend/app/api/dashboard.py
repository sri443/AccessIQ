from fastapi import APIRouter, HTTPException
from app.api.analysis import ANALYZED_USERS
from app.models.schemas import DashboardSummary, UserSummary

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary() -> DashboardSummary:
    if not ANALYZED_USERS: raise HTTPException(400, "Please run analysis first")
    critical = sum(1 for u in ANALYZED_USERS if u['risk_level'] == 'Critical')
    high = sum(1 for u in ANALYZED_USERS if u['risk_level'] == 'High')
    medium = sum(1 for u in ANALYZED_USERS if u['risk_level'] == 'Medium')
    low = sum(1 for u in ANALYZED_USERS if u['risk_level'] == 'Low')
    
    top_risks = [UserSummary(id=u['id'], name=u['name'], department=u['department'], role=u['role'], account_type=u['account_type'], risk_score=u['risk_score'], risk_level=u['risk_level'], color=u['color'], bg_color=u['bg_color'], primary_finding=u['findings'][0]['type'] if u['findings'] else None) for u in ANALYZED_USERS[:5]]
    
    return DashboardSummary(total_users=len(ANALYZED_USERS), critical_count=critical, high_count=high, medium_count=medium, low_count=low, compliance_score=max(0, 100 - (critical * 5 + high * 3 + medium * 2)), total_violations=critical + high + medium, top_risks=top_risks)