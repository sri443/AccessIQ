from typing import Dict, Any, List
from app.services.data_processor import DataProcessor


class ExplainabilityEngine:
    """Generates human-readable narratives and recommendations."""
    
    @classmethod
    def generate_narrative(cls, user_data: Dict[str, Any], findings: List[Dict], 
                          context_modifiers: List[str], risk_score: int, risk_level: str) -> str:
        """Generate explainable AI narrative for risk assessment."""
        
        narrative_parts = [f"This account is classified as {risk_level} with a risk score of {risk_score}/100."]
        
        # Add finding descriptions
        if findings:
            finding_descriptions = [f['description'] for f in findings]
            narrative_parts.append(f"Primary risk drivers: {' '.join(finding_descriptions)}")
        
        # Add context modifiers
        if context_modifiers:
            narrative_parts.append(f"Context adjustments applied: {' '.join(context_modifiers)}")
        
        return ' '.join(narrative_parts)
    
    @classmethod
    def calculate_blast_radius(cls, user_data: Dict[str, Any]) -> str:
        """Calculate potential blast radius if account is compromised."""
        user_systems = user_data.get('systems', [])
        sensitive_systems = DataProcessor.get_sensitive_systems()
        
        sensitive_exposed = [s for s in user_systems if s in sensitive_systems]
        
        if sensitive_exposed:
            return f"Compromise exposes {len(sensitive_exposed)} sensitive systems: {', '.join(sensitive_exposed)}. Potential for lateral movement."
        else:
            return "Limited lateral movement potential. Account has minimal access to sensitive systems."
    
    @classmethod
    def generate_recommendations(cls, user_data: Dict[str, Any], findings: List[Dict], 
                                risk_level: str) -> List[str]:
        """Generate remediation recommendations."""
        recommendations = []
        
        finding_types = [f['type'] for f in findings]
        
        if risk_level in ['Critical', 'High']:
            recommendations.append("Immediate security review required")
            recommendations.append("Consider temporary account suspension pending review")
        
        if 'Stale Account' in finding_types or 'Stale Admin' in finding_types:
            recommendations.append("Disable account and review access requirements")
        
        if 'Over-Privileged' in finding_types:
            recommendations.append("Conduct access review and remove unnecessary permissions")
        
        if 'Orphan Service Account' in finding_types:
            recommendations.append("Assign owner to service account and document purpose")
        
        if 'Cross-Department Access' in finding_types:
            recommendations.append("Review cross-department access justification with department heads")
        
        if 'Privilege Abuse Pattern' in finding_types:
            recommendations.append("Investigate access patterns and implement enhanced monitoring")
        
        if not recommendations:
            recommendations.append("Continue standard monitoring and periodic access reviews")
        
        return recommendations