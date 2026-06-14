from typing import Dict, Any, List
from collections import defaultdict
import math

class HackathonMetrics:
    @classmethod
    def calculate_all_metrics(cls, analyzed_users: List[Dict]) -> Dict[str, Any]:
        if not analyzed_users: return {}
        return {
            "top_risky_users": cls._top_risky_users(analyzed_users),
            "department_risk_ranking": cls._department_risk_ranking(analyzed_users),
            "compliance_score": cls._compliance_score(analyzed_users),
            "risk_trend_metrics": cls._risk_trend_metrics(analyzed_users)
        }

    @classmethod
    def _top_risky_users(cls, users: List[Dict], top_n: int = 10) -> List[Dict]:
        return [{"rank": i+1, "user_id": u.get('id'), "name": u.get('name'), "risk_score": u.get('risk_score', 0), "risk_level": u.get('risk_level')} for i, u in enumerate(sorted(users, key=lambda x: x.get('risk_score', 0), reverse=True)[:top_n])]

    @classmethod
    def _department_risk_ranking(cls, users: List[Dict]) -> List[Dict]:
        dept_stats = defaultdict(lambda: {'users': 0, 'total_risk': 0, 'critical_count': 0})
        for u in users:
            dept = u.get('department', 'Unassigned')
            dept_stats[dept]['users'] += 1
            dept_stats[dept]['total_risk'] += u.get('risk_score', 0)
            if u.get('risk_level') == 'Critical': dept_stats[dept]['critical_count'] += 1
        
        results = []
        for dept, stats in dept_stats.items():
            avg_risk = stats['total_risk'] / stats['users'] if stats['users'] > 0 else 0
            results.append({"department": dept, "avg_user_risk": round(avg_risk, 1), "critical_users": stats['critical_count'], "total_users": stats['users']})
        return sorted(results, key=lambda x: x['avg_user_risk'], reverse=True)

    @classmethod
    def _compliance_score(cls, users: List[Dict]) -> Dict[str, Any]:
        total = sum(len(u.get('findings', [])) for u in users)
        critical = sum(1 for u in users for f in u.get('findings', []) if f.get('points', 0) > 30)
        score = max(0, 100 - (total * 3) - (critical * 10))
        return {"overall_score": score, "total_findings": total, "critical_violations": critical}

    @classmethod
    def _risk_trend_metrics(cls, users: List[Dict]) -> Dict[str, Any]:
        scores = [u.get('risk_score', 0) for u in users]
        avg = sum(scores) / len(scores) if scores else 0
        return {
            "average_risk_score": round(avg, 1),
            "highest_risk_score": max(scores) if scores else 0,
            "risk_distribution": {
                'critical': sum(1 for s in scores if s >= 76),
                'high': sum(1 for s in scores if 51 <= s < 76),
                'medium': sum(1 for s in scores if 26 <= s < 51),
                'low': sum(1 for s in scores if s < 26)
            }
        }