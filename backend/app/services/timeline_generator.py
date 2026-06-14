from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pandas as pd

class EventCategory(Enum):
    ACCOUNT_CREATION = "account_creation"; PRIVILEGE_CHANGE = "privilege_change"; SUSPICIOUS_ACCESS = "suspicious_access"
    INACTIVITY_START = "inactivity_start"; PASSWORD_CHANGE = "password_change"; ROLE_CHANGE = "role_change"
    DEPARTMENT_CHANGE = "department_change"; ACCESS_GRANTED = "access_granted"; ACCESS_REVOKED = "access_revoked"
    SECURITY_INCIDENT = "security_incident"; AUDIT_EVENT = "audit_event"

@dataclass
class TimelineEvent:
    timestamp: datetime; category: EventCategory; description: str; severity: str; details: Dict[str, Any]; risk_impact: int

class TimelineGenerator:
    @classmethod
    def generate_timeline(cls, user_data: Dict[str, Any], events_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        events = []
        joined = cls._parse_date(user_data.get('joined_date'))
        if joined: events.append(TimelineEvent(joined, EventCategory.ACCOUNT_CREATION, f"Account created for {user_data.get('name')}", "info", {}, 0))
        
        last_login = cls._parse_date(user_data.get('last_login'))
        if last_login:
            days_inactive = user_data.get('days_since_login', 0)
            sev = "critical" if days_inactive > 90 else "warning" if days_inactive > 30 else "info"
            events.append(TimelineEvent(last_login, EventCategory.SUSPICIOUS_ACCESS if days_inactive > 30 else EventCategory.AUDIT_EVENT, f"Last activity ({days_inactive} days ago)", sev, {"days_inactive": days_inactive}, min(50, days_inactive // 2)))
        
        if events_df is not None and len(events_df) > 0:
            user_events = events_df[events_df['user_id'] == user_data.get('id')]
            events.extend(cls._process_real_events(user_events))
            
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return {
            "user_id": user_data.get('id'), "user_name": user_data.get('name'), "total_events": len(events),
            "timeline": [{"timestamp": e.timestamp.isoformat() if hasattr(e.timestamp, 'isoformat') else str(e.timestamp), "category": e.category.value, "description": e.description, "severity": e.severity, "risk_impact": e.risk_impact, "details": e.details} for e in events],
            "critical_events": len([e for e in events if e.severity == 'critical']),
            "risk_trajectory": cls._calculate_risk_trajectory(events),
            "key_findings": [f"Account inactive for {user_data.get('days_since_login')} days"] if user_data.get('days_since_login', 0) > 90 else []
        }

    @classmethod
    def _parse_date(cls, date_value: Any) -> Optional[datetime]:
        if not date_value: return None
        if isinstance(date_value, datetime): return date_value
        try: return pd.to_datetime(date_value).to_pydatetime()
        except: return None

    @classmethod
    def _process_real_events(cls, user_events: pd.DataFrame) -> List[TimelineEvent]:
        timeline = []
        if 'timestamp' not in user_events.columns: return timeline
        for _, event in user_events.sort_values('timestamp', ascending=False).head(20).iterrows():
            ts = cls._parse_date(event.get('timestamp'))
            if ts: timeline.append(TimelineEvent(ts, EventCategory.AUDIT_EVENT, f"{event.get('event_type')}: {event.get('system')}", "info", event.to_dict(), 0))
        return timeline
    
    @classmethod
    def _calculate_risk_trajectory(cls, events: List[TimelineEvent]) -> List[Dict[str, Any]]:
        trajectory = []; cumulative_risk = 0
        for event in sorted(events, key=lambda e: e.timestamp):
            cumulative_risk = min(100, cumulative_risk + event.risk_impact)
            trajectory.append({"timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, 'isoformat') else str(event.timestamp), "risk_score": cumulative_risk, "event": event.description[:50]})
        return trajectory[-20:]