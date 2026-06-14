from fastapi import APIRouter, HTTPException
from app.api.analysis import ANALYZED_USERS
from app.compliance.compliance_mapper import ComplianceMapper
from app.models.schemas import ComplianceReport

router = APIRouter()

@router.get("/")
async def get_compliance_report() -> ComplianceReport:
    if not ANALYZED_USERS: raise HTTPException(400, "Please run analysis first")
    
    all_findings = []
    for user in ANALYZED_USERS: all_findings.extend(user['findings'])
    
    unique_findings = {}
    for finding in all_findings:
        if finding['type'] not in unique_findings: unique_findings[finding['type']] = finding
        else: unique_findings[finding['type']]['confidence'] = max(unique_findings[finding['type']]['confidence'], finding['confidence'])

    compliance_data = ComplianceMapper.get_framework_summary(list(unique_findings.values()))
    return ComplianceReport(violations=compliance_data['violations'], compliance_score=compliance_data['compliance_score'], framework_mappings=compliance_data['framework_counts'])