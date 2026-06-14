from typing import Dict, Any, List, Tuple
from app.models.schemas import RiskLevel

class RiskScorer:
    @staticmethod
    def calculate_score(findings: List[Dict[str, Any]]) -> Tuple[int, float]:
        if not findings: return 0, 1.0
        total_points = sum(finding.get('points', 0) for finding in findings)
        avg_confidence = sum(finding.get('confidence', 1.0) for finding in findings) / len(findings)
        return min(100, total_points), avg_confidence

    @staticmethod
    def classify_risk(score: int) -> Tuple[RiskLevel, str, str]:
        if score >= 76: return RiskLevel.CRITICAL, 'text-red-500', 'bg-red-500/10'
        elif score >= 51: return RiskLevel.HIGH, 'text-orange-400', 'bg-orange-500/10'
        elif score >= 26: return RiskLevel.MEDIUM, 'text-yellow-400', 'bg-yellow-500/10'
        else: return RiskLevel.LOW, 'text-green-400', 'bg-green-500/10'

    @classmethod
    def calculate_weighted_score(cls, findings: List[Dict], baseline_score: float, blast_radius_score: float, context_modifier: float) -> Dict[str, Any]:
        base_score, confidence = cls.calculate_score(findings)
        weights = {'findings': 0.45, 'baseline': 0.20, 'blast_radius': 0.25, 'context': 0.10}
        normalized_context = abs(context_modifier)
        
        final_score = (
            weights['findings'] * base_score +
            weights['baseline'] * (baseline_score or 0) +
            weights['blast_radius'] * (blast_radius_score or 0) +
            weights['context'] * normalized_context
        )
        final_score = min(100, round(final_score))
        risk_level, color, bg_color = cls.classify_risk(final_score)
        
        return {
            'risk_score': final_score, 'confidence': confidence, 'risk_level': risk_level.value if hasattr(risk_level, 'value') else risk_level,
            'color': color, 'bg_color': bg_color,
            'score_breakdown': {
                'findings_contribution': round(weights['findings'] * base_score, 1),
                'baseline_contribution': round(weights['baseline'] * (baseline_score or 0), 1),
                'blast_radius_contribution': round(weights['blast_radius'] * (blast_radius_score or 0), 1),
                'context_contribution': round(weights['context'] * normalized_context, 1)
            }
        }