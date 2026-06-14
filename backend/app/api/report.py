from fastapi import APIRouter, HTTPException
from app.api.analysis import ANALYZED_USERS
from app.compliance.compliance_mapper import ComplianceMapper
from datetime import datetime

router = APIRouter()

@router.get("/{user_id}")
async def generate_report(user_id: str):
    if not ANALYZED_USERS: raise HTTPException(400, "Please run analysis first")
    user = next((u for u in ANALYZED_USERS if u['id'] == user_id), None)
    if not user: raise HTTPException(404, "User not found")

    compliance_mappings = []
    for finding in user['findings']:
        mappings = ComplianceMapper.map_finding_to_compliance(finding['type'])
        compliance_mappings.extend([m.dict() for m in mappings])

    return {
        "report_id": f"RPT-{user['id']}",
        "generated_at": datetime.now().isoformat(),
        "user": {"id": user['id'], "name": user['name'], "department": user['department'], "role": user['role'], "account_type": user['account_type']},
        "risk_assessment": {"score": user['risk_score'], "level": user['risk_level'], "narrative": user['narrative']},
        "findings": user['findings'],
        "compliance_mappings": compliance_mappings,
        "recommendations": user['recommendations']
    }