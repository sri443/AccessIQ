from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class AssetSensitivity(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

@dataclass
class ExposedAsset:
    name: str
    sensitivity: AssetSensitivity
    data_types: List[str]
    blast_multiplier: float

class BlastRadiusAnalyzer:
    ASSET_CLASSIFICATION = {
        'AWS': ExposedAsset('AWS', AssetSensitivity.CRITICAL, ['Credentials', 'Infrastructure', 'Secrets'], 3.0),
        'AzureAD': ExposedAsset('AzureAD', AssetSensitivity.CRITICAL, ['Identity', 'Authentication', 'SSO'], 2.8),
        'FinanceDB': ExposedAsset('FinanceDB', AssetSensitivity.CRITICAL, ['Financial Records', 'PII', 'Payment Data'], 3.5),
        'HRDB': ExposedAsset('HRDB', AssetSensitivity.CRITICAL, ['Employee PII', 'Salary Data', 'Performance Reviews'], 3.2),
        'Payroll': ExposedAsset('Payroll', AssetSensitivity.CRITICAL, ['Banking Info', 'Salary', 'Tax Information'], 3.8),
        'ERP': ExposedAsset('ERP', AssetSensitivity.HIGH, ['Business Data', 'Inventory', 'Procurement'], 2.0),
        'GitHub': ExposedAsset('GitHub', AssetSensitivity.HIGH, ['Source Code', 'IP', 'Secrets'], 2.5),
        'CI/CD': ExposedAsset('CI/CD', AssetSensitivity.HIGH, ['Build Pipeline', 'Deployment Keys', 'Artifacts'], 2.3),
        'SIEM': ExposedAsset('SIEM', AssetSensitivity.MEDIUM, ['Security Logs', 'Alerts', 'Monitoring'], 1.5),
        'VPN': ExposedAsset('VPN', AssetSensitivity.MEDIUM, ['Network Access', 'Internal Routing'], 1.8),
    }

    @classmethod
    def calculate_blast_radius(cls, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_systems = user_data.get('systems', [])
        account_type = user_data.get('account_type', 'Employee')
        
        exposed_assets = [
            cls.ASSET_CLASSIFICATION.get(s, ExposedAsset(s, AssetSensitivity.MEDIUM, ['Unknown'], 1.0)) 
            for s in user_systems
        ]
        
        privilege_concentration = cls._calculate_privilege_concentration(user_data)
        lateral_risk = cls._calculate_lateral_movement_risk(user_data, exposed_assets)
        blast_score = cls._calculate_blast_score(exposed_assets, privilege_concentration, lateral_risk, account_type)
        
        return {
            "blast_radius_score": blast_score,
            "exposed_assets": [
                {
                    "name": a.name, 
                    "sensitivity": a.sensitivity.value, 
                    "sensitivity_label": a.sensitivity.name, 
                    "data_types": a.data_types, 
                    "blast_multiplier": a.blast_multiplier
                } for a in exposed_assets
            ],
            "privilege_concentration": privilege_concentration, 
            "lateral_movement_risk": lateral_risk,
            "sensitive_systems_exposed": len([a for a in exposed_assets if a.sensitivity in [AssetSensitivity.CRITICAL, AssetSensitivity.HIGH]]),
            "data_types_exposed": list(set(data_type for asset in exposed_assets for data_type in asset.data_types)),
            "risk_summary": cls._generate_risk_summary(exposed_assets, privilege_concentration, lateral_risk, user_data),
            "mitigation_priority": "CRITICAL" if blast_score >= 80 else "HIGH" if blast_score >= 60 else "MEDIUM" if blast_score >= 40 else "LOW"
        }

    @classmethod
    def _calculate_privilege_concentration(cls, user_data: Dict[str, Any]) -> int:
        systems = user_data.get('systems', [])
        if not systems: 
            return 0
            
        sensitive = len([
            s for s in systems 
            if s in cls.ASSET_CLASSIFICATION and cls.ASSET_CLASSIFICATION[s].sensitivity in [AssetSensitivity.CRITICAL, AssetSensitivity.HIGH]
        ])
        
        ratio = sensitive / len(systems)
        priv_factor = 1.5 if user_data.get('privilege_level', '').lower() in ['admin', 'elevated', 'high'] else (1.3 if 'admin' in user_data.get('role', '').lower() else 1.0)
        
        return min(100, round(ratio * 60 + min(40, len(systems) * 5) + (priv_factor - 1) * 50))

    @classmethod
    def _calculate_lateral_movement_risk(cls, user_data: Dict[str, Any], exposed_assets: List[ExposedAsset]) -> int:
        if not exposed_assets:
            return 0

        total_risk = sum(asset.sensitivity.value * asset.blast_multiplier for asset in exposed_assets)
        actual_max = len(exposed_assets) * AssetSensitivity.CRITICAL.value * 3.8

        if actual_max <= 0:
            return 0

        risk_score = (total_risk / actual_max) * 100
        systems = user_data.get("systems", [])

        if user_data.get("department") == "Finance" and any("HR" in system for system in systems):
            risk_score += 15

        return min(100, round(risk_score))

    @classmethod
    def _calculate_blast_score(cls, exposed_assets, privilege_concentration, lateral_risk, account_type) -> int:
        asset_risk = min(100, sum(a.sensitivity.value * a.blast_multiplier for a in exposed_assets) * 10)
        score = (0.4 * asset_risk + 0.35 * privilege_concentration + 0.25 * lateral_risk)
        
        if account_type == 'Service': 
            score *= 1.2
            
        return min(100, round(score))

    @classmethod
    def _generate_risk_summary(cls, exposed_assets, privilege_concentration, lateral_risk, user_data) -> str:
        critical_assets = [a.name for a in exposed_assets if a.sensitivity == AssetSensitivity.CRITICAL]
        parts = []
        
        if critical_assets: 
            parts.append(f"Compromise would expose {len(critical_assets)} critical systems: {', '.join(critical_assets[:3])}")
        if privilege_concentration > 70: 
            parts.append(f"High privilege concentration ({privilege_concentration}%) increases blast radius")
        if lateral_risk > 70: 
            parts.append(f"Significant lateral movement potential (risk: {lateral_risk}%)")
            
        return '. '.join(parts) + '.' if parts else "Limited blast radius. Minimal access to critical systems."