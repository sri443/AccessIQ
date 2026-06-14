from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Finding(BaseModel):
    type: str
    description: str
    points: int
    confidence: float = 1.0

class ComplianceMapping(BaseModel):
    standard: str
    control: str
    severity: str
    description: str
    recommendation: str

class UserSummary(BaseModel):
    id: str
    name: str
    department: str
    role: str
    account_type: str
    risk_score: int
    risk_level: RiskLevel
    color: str
    bg_color: str
    primary_finding: Optional[str] = None

class DashboardSummary(BaseModel):
    total_users: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    compliance_score: float
    total_violations: int
    top_risks: List[UserSummary]

class GraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class ComplianceReport(BaseModel):
    violations: List[Dict[str, Any]]
    compliance_score: float
    framework_mappings: Dict[str, List[Dict[str, Any]]]

class AnalysisResponse(BaseModel):
    status: str
    users_processed: int
    summary: DashboardSummary

class BlastRadiusData(BaseModel):
    blast_radius_score: int = 0
    exposed_assets: List[Dict[str, Any]] = Field(default_factory=list)
    privilege_concentration: int = 0
    lateral_movement_risk: int = 0
    sensitive_systems_exposed: int = 0
    data_types_exposed: List[str] = Field(default_factory=list)
    risk_summary: str = ""
    mitigation_priority: str = ""

class BaselineDeviation(BaseModel):
    baseline_score: int = 0
    deviation_details: Dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    confidence: float = 0.0

class ScoreBreakdown(BaseModel):
    findings_contribution: float = 0.0
    baseline_contribution: float = 0.0
    blast_radius_contribution: float = 0.0
    context_contribution: float = 0.0

class TimelineEvent(BaseModel):
    timestamp: str
    category: str
    description: str
    severity: str
    risk_impact: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)

class Timeline(BaseModel):
    user_id: str
    user_name: str
    total_events: int = 0
    timeline: List[TimelineEvent] = Field(default_factory=list)
    critical_events: int = 0
    risk_trajectory: List[Dict[str, Any]] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)

class UserDetail(BaseModel):
    id: str
    name: str
    department: str
    role: str
    account_type: str
    joined_date: str
    last_login: Optional[str] = None
    systems: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    risk_score: int
    risk_level: str
    color: str
    bg_color: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_violations: List[str] = Field(default_factory=list)
    narrative: str
    detailed_analysis: Optional[str] = None
    impact_assessment: Optional[str] = None
    blast_radius: Optional[Dict[str, Any]] = None
    blast_radius_score: int = 0
    blast_radius_summary: str = ""
    baseline_score: int = 0
    baseline_deviation: str = ""
    recommendations: List[str] = Field(default_factory=list)
    context_modifiers: List[str] = Field(default_factory=list)
    score_breakdown: Optional[Dict[str, Any]] = None
    context_confidence: float = 1.0
    baseline_confidence: float = 0.0

class HackathonMetrics(BaseModel):
    top_risky_users: List[Dict[str, Any]] = Field(default_factory=list)
    top_violated_controls: List[Dict[str, Any]] = Field(default_factory=list)
    department_risk_ranking: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_score: Dict[str, Any] = Field(default_factory=dict)
    risk_trend_metrics: Dict[str, Any] = Field(default_factory=dict)
    privilege_concentration_index: Dict[str, Any] = Field(default_factory=dict)
    remediation_backlog: Dict[str, Any] = Field(default_factory=dict)
    risk_heatmap_data: Dict[str, Any] = Field(default_factory=dict)
    key_risk_indicators: List[Dict[str, Any]] = Field(default_factory=list)