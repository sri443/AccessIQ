from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import calendar

class ContextCategory(Enum):
    EXECUTIVE_EXCEPTION = "executive_exception"
    SABBATICAL_APPROVED = "sabbatical_approved"
    CONTRACT_ENDED = "contract_ended"
    NEW_HIRE_ONBOARDING = "new_hire_onboarding"
    TEMP_PRIVILEGE = "temp_privilege"
    MONTH_END_FINANCE = "month_end_finance"
    QUARTER_END_AUDIT = "quarter_end_audit"
    MAINTENANCE_WINDOW = "maintenance_window"
    INCIDENT_RESPONSE = "incident_response"
    VENDOR_ACCESS = "vendor_access"

@dataclass
class ContextRule:
    category: ContextCategory
    priority: int
    risk_modifier: int
    confidence_threshold: float
    conditions: Dict[str, Any]
    explanation_template: str

class ContextEngine:
    CONTEXT_RULES = [
        ContextRule(category=ContextCategory.EXECUTIVE_EXCEPTION, priority=1, risk_modifier=-50, confidence_threshold=0.85, conditions={'roles': ['CTO', 'CISO', 'CIO', 'CEO', 'COO', 'VP', 'Director'], 'max_modifier_per_condition': -50}, explanation_template="Executive role '{role}': Broad system access is expected and governed by board-level oversight"),
        ContextRule(category=ContextCategory.SABBATICAL_APPROVED, priority=2, risk_modifier=-35, confidence_threshold=0.90, conditions={'account_types': ['Employee'], 'min_tenure_days': 365, 'max_inactivity_days': 180, 'requires_justification': True}, explanation_template="Approved sabbatical leave: Account inactive for {days} days with proper HR documentation"),
        ContextRule(category=ContextCategory.CONTRACT_ENDED, priority=3, risk_modifier=25, confidence_threshold=0.75, conditions={'account_types': ['Contractor'], 'max_inactivity_days': 20, 'check_contract_status': True}, explanation_template="Contractor account inactive {days} days post-contract: Requires immediate offboarding verification"),
        ContextRule(category=ContextCategory.NEW_HIRE_ONBOARDING, priority=4, risk_modifier=-30, confidence_threshold=0.80, conditions={'max_tenure_days': 30, 'account_types': ['Employee', 'Contractor'], 'elevated_privileges_allowed': False}, explanation_template="New hire onboarding (Day {days}): Access patterns being established under supervision"),
        ContextRule(category=ContextCategory.TEMP_PRIVILEGE, priority=5, risk_modifier=-20, confidence_threshold=0.70, conditions={'requires_ticket_reference': True, 'max_duration_hours': 8, 'approval_required': True}, explanation_template="Temporary privilege elevation for approved change window: Ticket #{ticket}"),
        ContextRule(category=ContextCategory.MONTH_END_FINANCE, priority=6, risk_modifier=-15, confidence_threshold=0.75, conditions={'departments': ['Finance', 'Accounting'], 'month_end_days': 3, 'expected_behavior': 'increased_system_access'}, explanation_template="Month-end financial closing: Elevated access patterns expected for {department}"),
        ContextRule(category=ContextCategory.QUARTER_END_AUDIT, priority=7, risk_modifier=-25, confidence_threshold=0.80, conditions={'departments': ['Finance', 'Compliance', 'Audit'], 'quarter_end_days': 5, 'expected_behavior': 'cross_department_access'}, explanation_template="Quarter-end audit period: Cross-department data access required for compliance verification"),
        ContextRule(category=ContextCategory.MAINTENANCE_WINDOW, priority=8, risk_modifier=-15, confidence_threshold=0.65, conditions={'roles': ['DevOps Engineer', 'System Administrator', 'SRE'], 'off_hours_access': True, 'expected_systems': ['AWS', 'CI/CD', 'Production']}, explanation_template="Scheduled maintenance window: Elevated system access within approved change window"),
        ContextRule(category=ContextCategory.INCIDENT_RESPONSE, priority=9, risk_modifier=-40, confidence_threshold=0.90, conditions={'roles': ['Security Analyst', 'SOC Analyst', 'Incident Responder'], 'emergency_access': True, 'time_bound': True}, explanation_template="Active incident response: Emergency access granted under IR protocol #{incident_id}"),
        ContextRule(category=ContextCategory.VENDOR_ACCESS, priority=10, risk_modifier=-10, confidence_threshold=0.60, conditions={'account_types': ['Service', 'External'], 'vendor_managed': True, 'periodic_review_required': True}, explanation_template="Vendor-managed service account: Access governed by SLA and periodic access review")
    ]

    @classmethod
    def evaluate_context(cls, user_data: Dict[str, Any], risk_score: int, findings: List[Dict], simulation_date: Optional[datetime] = None) -> Tuple[int, List[str], float]:
        applied_contexts = []
        total_modifier = 0
        confidence_scores = []
        sorted_rules = sorted(cls.CONTEXT_RULES, key=lambda x: x.priority)
        
        for rule in sorted_rules:
            if cls._rule_applies(rule, user_data, findings, simulation_date):
                modifier = cls._calculate_modifier(rule, user_data, risk_score)
                total_modifier += modifier
                confidence_scores.append(rule.confidence_threshold)
                applied_contexts.append(cls._format_explanation(rule, user_data))
                
        adjusted_score = max(0, min(100, risk_score + total_modifier))
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0
        return adjusted_score, applied_contexts, overall_confidence

    @classmethod
    def _rule_applies(cls, rule: ContextRule, user_data: Dict[str, Any], findings: List[Dict], simulation_date: Optional[datetime] = None) -> bool:
        conditions = rule.conditions
        today = simulation_date or datetime.now()
        
        if 'roles' in conditions and user_data.get('role') not in conditions['roles']: return False
        if 'account_types' in conditions and user_data.get('account_type') not in conditions['account_types']: return False
        if 'departments' in conditions and user_data.get('department') not in conditions['departments']: return False
        if 'min_tenure_days' in conditions and user_data.get('days_since_joined', 0) < conditions['min_tenure_days']: return False
        if 'max_tenure_days' in conditions and user_data.get('days_since_joined', 0) > conditions['max_tenure_days']: return False
        if 'max_inactivity_days' in conditions and user_data.get('days_since_login', 0) > conditions['max_inactivity_days']: return False
        
        if 'elevated_privileges_allowed' in conditions:
            if not conditions['elevated_privileges_allowed']:
                privilege_findings = [f for f in findings if 'privilege' in f['type'].lower()]
                if privilege_findings and user_data.get('days_since_joined', 365) <= 30: return False
                if not privilege_findings: return True
            
        if 'month_end_days' in conditions:
            days_in_month = calendar.monthrange(today.year, today.month)[1]
            threshold = days_in_month - conditions['month_end_days'] + 1
            return today.day >= threshold

        if 'quarter_end_days' in conditions:
            if today.month not in [3, 6, 9, 12]:
                return False
            days_in_month = calendar.monthrange(today.year, today.month)[1]
            threshold = days_in_month - conditions['quarter_end_days'] + 1
            return today.day >= threshold
            
        return True

    @classmethod
    def _calculate_modifier(cls, rule: ContextRule, user_data: Dict[str, Any], risk_score: int) -> int:
        base_modifier = rule.risk_modifier
        if risk_score > 75 and base_modifier < 0: base_modifier = int(base_modifier * 0.5)
        elif risk_score < 25 and base_modifier > 0: base_modifier = int(base_modifier * 0.7)
        max_mod = rule.conditions.get('max_modifier_per_condition')
        if max_mod and abs(base_modifier) > abs(max_mod): base_modifier = max_mod if base_modifier > 0 else -abs(max_mod)
        return base_modifier

    @classmethod
    def _format_explanation(cls, rule: ContextRule, user_data: Dict[str, Any]) -> str:
        return rule.explanation_template.format(
            role=user_data.get('role', 'User'), days=user_data.get('days_since_login', 0),
            department=user_data.get('department', 'Unknown'), ticket=user_data.get('ticket_reference', 'N/A'),
            incident_id=user_data.get('incident_id', 'N/A')
        )