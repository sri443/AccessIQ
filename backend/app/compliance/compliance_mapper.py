from typing import Dict, Any, List
from app.models.schemas import ComplianceMapping

class ComplianceMapper:
    COMPLIANCE_MAP = {
        'Stale Account': {'standards': ['NIST AC-2'], 'severity': 'High', 'description': 'Inactive account control', 'recommendation': 'Disable account'},
        'Over-Privileged': {'standards': ['NIST AC-6', 'GDPR Art 32'], 'severity': 'High', 'description': 'Least privilege violation', 'recommendation': 'Review access'},
        'Orphan Service Account': {'standards': ['NIST IA-4'], 'severity': 'Critical', 'description': 'Identifier management', 'recommendation': 'Assign owner'},
        'Cross-Department Access': {'standards': ['NIST AC-3'], 'severity': 'Medium', 'description': 'Access control', 'recommendation': 'Review justification'}
    }

    @classmethod
    def map_finding_to_compliance(cls, finding_type: str) -> List[ComplianceMapping]:
        mapping = cls.COMPLIANCE_MAP.get(finding_type)
        if not mapping:
            return [ComplianceMapping(standard='NIST AC-2', control='Account Management', severity='Low', description='General access violation', recommendation='Review access')]
        return [ComplianceMapping(standard=s, control=s.split(' ')[-1], severity=mapping['severity'], description=mapping['description'], recommendation=mapping['recommendation']) for s in mapping['standards']]

    @classmethod
    def get_framework_summary(cls, findings: List[Dict]) -> Dict[str, Any]:
        violations = []; framework_counts = {}
        for finding in findings:
            mappings = cls.map_finding_to_compliance(finding['type'])
            for mapping in mappings:
                violations.append(mapping.dict())
                if mapping.standard not in framework_counts: framework_counts[mapping.standard] = {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                framework_counts[mapping.standard]['total'] += 1
                sev_key = mapping.severity.lower()
                if sev_key in framework_counts[mapping.standard]: framework_counts[mapping.standard][sev_key] += 1
        
        comp_score = max(0, min(100, 100 - (len(violations) * 5)))
        return {'violations': violations, 'compliance_score': comp_score, 'total_violations': len(violations), 'framework_counts': framework_counts}