from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class RiskNarrative:
    executive_summary: str; detailed_analysis: str; impact_assessment: str; remediation_plan: List[str]; technical_details: Dict[str, Any]

class RiskExplanationEngine:
    @classmethod
    def generate_full_explanation(cls, user_data: Dict[str, Any], findings: List[Dict], context_applied: List[str], blast_radius: Dict[str, Any], baseline_data: Dict[str, Any]) -> RiskNarrative:
        return RiskNarrative(
            executive_summary=cls._generate_executive_summary(user_data, findings, blast_radius),
            detailed_analysis=cls._generate_detailed_analysis(user_data, findings, context_applied),
            impact_assessment=cls._generate_impact_assessment(user_data, blast_radius, baseline_data),
            remediation_plan=cls._generate_remediation_plan(user_data, findings),
            technical_details={"risk_score": user_data.get('risk_score', 0)}
        )

    @classmethod
    def _generate_executive_summary(cls, user_data, findings, blast_radius) -> str:
        parts = [f"{user_data.get('name')} ({user_data.get('role')}) has a {user_data.get('risk_level')} risk score of {user_data.get('risk_score')}/100."]
        if any('Stale' in f['type'] for f in findings): parts.append(f"Account inactive for {user_data.get('days_since_login', 0)} days.")
        if any('Over-Privileged' in f['type'] for f in findings): parts.append(f"User has privileges across {len(user_data.get('systems', []))} systems.")
        if blast_radius.get('blast_radius_score', 0) > 50: parts.append(f"Potential exposure includes {blast_radius.get('sensitive_systems_exposed', 0)} critical systems.")
        return ' '.join(parts)

    @classmethod
    def _generate_detailed_analysis(cls, user_data, findings, context_applied) -> str:
        sections = [f"ACCOUNT OVERVIEW: User: {user_data.get('name')}", f"RISK FINDINGS ({len(findings)} total):"]
        for i, finding in enumerate(findings, 1): sections.append(f"  {i}. [{finding.get('type')}] {finding.get('description')}")
        if context_applied:
            sections.append("\nCONTEXT ADJUSTMENTS:")
            for ctx in context_applied: sections.append(f"  • {ctx}")
        return '\n'.join(sections)

    @classmethod
    def _generate_impact_assessment(cls, user_data, blast_radius, baseline_data) -> str:
        sections = ["BUSINESS IMPACT ASSESSMENT:"]
        if blast_radius.get('data_types_exposed'): sections.append(f"• Data at Risk: {', '.join(blast_radius['data_types_exposed'])}")
        lat_risk = blast_radius.get('lateral_movement_risk', 0)
        if lat_risk > 50: sections.append(f"• Lateral Movement Risk: HIGH ({lat_risk}%)")
        return '\n'.join(sections)

    @classmethod
    def _generate_remediation_plan(cls, user_data, findings) -> List[str]:
        plan = []
        if user_data.get('risk_level') in ['Critical', 'High']:
            plan.append("IMMEDIATE (Within 24 hours):")
            if user_data.get('days_since_login', 0) > 30: plan.append("  1. Disable inactive account")
            if any('Privilege' in f.get('type', '') for f in findings): plan.append("  2. Revoke excessive privileges")
        plan.extend(["\nSHORT-TERM (Within 1 week):", "  1. Conduct comprehensive access review"])
        return plan