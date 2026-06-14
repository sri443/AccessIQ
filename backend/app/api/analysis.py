from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.api.upload import state
from app.services.data_processor import DataProcessor
from app.scoring.risk_scorer import RiskScorer

router = APIRouter()
ANALYZED_USERS = []

# Import detectors (these should exist)
from app.detection.stale_accounts import StaleAccountDetector
from app.detection.over_privileged import OverPrivilegedDetector
from app.detection.orphan_service import OrphanServiceDetector
from app.detection.cross_department import CrossDepartmentDetector
from app.detection.privilege_abuse import PrivilegeAbuseDetector

# Try to import new services, fall back gracefully
try:
    from app.services.context_engine import ContextEngine
    HAS_CONTEXT = True
except ImportError:
    HAS_CONTEXT = False

try:
    from app.services.behavioral_baseline import BehavioralBaseline
    HAS_BASELINE = True
except ImportError:
    HAS_BASELINE = False

try:
    from app.services.blast_radius_analyzer import BlastRadiusAnalyzer
    HAS_BLAST = True
except ImportError:
    HAS_BLAST = False

try:
    from app.services.risk_explanation import RiskExplanationEngine
    HAS_EXPLANATION = True
except ImportError:
    HAS_EXPLANATION = False


@router.post("/run")
async def run_analysis(simulation_date: Optional[str] = Query(None)):
    global ANALYZED_USERS
    
    if state.USER_DATA is None:
        raise HTTPException(400, "Please upload users CSV first")
    
    # Process user data
    users = DataProcessor.enrich_user_data(state.USER_DATA, state.EVENT_DATA)
    
    detectors = [
        StaleAccountDetector(),
        OverPrivilegedDetector(),
        OrphanServiceDetector(),
        CrossDepartmentDetector(),
        PrivilegeAbuseDetector(),
    ]
    
    analyzed_users = []
    
    for user in users:
        findings = []
        
        # Run detectors
        for detector in detectors:
            finding = detector.detect(user)
            if finding:
                findings.append(finding)
        
        # Score
        base_score, confidence = RiskScorer.calculate_score(findings)
        risk_level, color, bg_color = RiskScorer.classify_risk(base_score)
        
        # Context (if available)
        context_modifiers = []
        if HAS_CONTEXT:
            try:
                base_score, context_modifiers, _ = ContextEngine.evaluate_context(user, base_score, findings)
            except:
                pass
        
        # Build result
        analyzed_user = {
            **user,
            'findings': findings,
            'context_modifiers': context_modifiers,
            'risk_score': base_score,
            'risk_level': risk_level,
            'color': color,
            'bg_color': bg_color,
            'narrative': f"Risk score: {base_score}/100. Findings: {len(findings)}.",
            'recommendations': ['Review account'] if findings else ['No action needed'],
            'blast_radius_score': 0,
            'baseline_score': 0,
            'blast_radius': {},
        }
        analyzed_users.append(analyzed_user)
    
    analyzed_users.sort(key=lambda x: x['risk_score'], reverse=True)
    ANALYZED_USERS.clear()
    ANALYZED_USERS.extend(analyzed_users)
    
    critical = sum(1 for u in analyzed_users if u['risk_level'] == 'Critical')
    high = sum(1 for u in analyzed_users if u['risk_level'] == 'High')
    medium = sum(1 for u in analyzed_users if u['risk_level'] == 'Medium')
    low = sum(1 for u in analyzed_users if u['risk_level'] == 'Low')
    
    return {
        "status": "completed",
        "users_analyzed": len(analyzed_users),
        "summary": {
            "total_users": len(analyzed_users),
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "compliance_score": max(0, 100 - (critical * 5 + high * 3 + medium * 2)),
            "total_violations": critical + high + medium
        }
    }