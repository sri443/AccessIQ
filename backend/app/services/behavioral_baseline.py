import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class BaselineMetrics:
    avg_systems_accessed: float
    avg_daily_events: float
    avg_login_frequency: float
    std_systems: float
    std_events: float
    std_login: float
    sample_size: int
    confidence: float

class BehavioralBaseline:
    def __init__(self, events_df: Optional[pd.DataFrame] = None):
        self.events_df = events_df
        self.role_baselines: Dict[str, BaselineMetrics] = {}
        self.global_baseline: Optional[BaselineMetrics] = None
        if events_df is not None: 
            self._build_baselines()

    def _build_baselines(self):
        if self.events_df is None: 
            return
        required_cols = ['user_id', 'event_type', 'timestamp']
        if not all(col in self.events_df.columns for col in required_cols): 
            return
        if 'system' not in self.events_df.columns: 
            self.events_df['system'] = 'unknown'
        self.events_df['timestamp'] = pd.to_datetime(self.events_df['timestamp'])
        
        user_metrics = self._calculate_user_metrics()
        self.global_baseline = self._calculate_baseline_metrics(user_metrics, "global")
        
        if 'role' in self.events_df.columns:
            for role in self.events_df['role'].unique():
                role_users = self.events_df[self.events_df['role'] == role]['user_id'].unique()
                role_metrics = user_metrics[user_metrics['user_id'].isin(role_users)]
                if len(role_metrics) > 0:
                    self.role_baselines[role] = self._calculate_baseline_metrics(role_metrics, f"role_{role}")
        else:
            for system in self.events_df['system'].unique():
                system_events = self.events_df[self.events_df['system'] == system]
                system_user_metrics = self._calculate_user_metrics(system_events)
                if len(system_user_metrics) > 0:
                    self.role_baselines[f"system_{system}"] = self._calculate_baseline_metrics(system_user_metrics, f"system_{system}")

    def _calculate_user_metrics(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        df = df if df is not None else self.events_df

        if df is None or len(df) == 0:
            return pd.DataFrame()

        working_df = df.copy()
        working_df["event_date"] = pd.to_datetime(working_df["timestamp"]).dt.date

        user_stats = (
            working_df
            .groupby("user_id")
            .agg(
                unique_systems=("system", "nunique"),
                total_events=("event_type", "count"),
                first_seen=("timestamp", "min"),
                last_seen=("timestamp", "max"),
                active_days=("event_date", "nunique")
            )
            .reset_index()
        )

        user_stats["days_active"] = (user_stats["last_seen"] - user_stats["first_seen"]).dt.days + 1
        user_stats["days_active"] = user_stats["days_active"].clip(lower=1)
        user_stats["avg_daily_events"] = user_stats["total_events"] / user_stats["days_active"]
        user_stats["login_frequency"] = user_stats["active_days"] / user_stats["days_active"]

        return user_stats

    def _calculate_baseline_metrics(self, user_metrics: pd.DataFrame, label: str) -> BaselineMetrics:
        if len(user_metrics) == 0: 
            return BaselineMetrics(0, 0, 0, 0, 0, 0, 0, 0.0)
        return BaselineMetrics(
            avg_systems_accessed=float(user_metrics['unique_systems'].mean()),
            avg_daily_events=float(user_metrics['avg_daily_events'].mean()),
            avg_login_frequency=float(user_metrics['login_frequency'].mean()),
            std_systems=float(user_metrics['unique_systems'].std() or 0.0),
            std_events=float(user_metrics['avg_daily_events'].std() or 0.0),
            std_login=float(user_metrics['login_frequency'].std() or 0.0),
            sample_size=len(user_metrics),
            confidence=min(1.0, len(user_metrics) / 30)
        )

    def calculate_deviation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.global_baseline:
            return {"baseline_score": 0, "deviation_details": {}, "reason": "Insufficient historical data", "confidence": 0.0}
        
        user_systems = len(user_data.get('systems', []))
        user_events = user_data.get('event_count', 0)
        user_days = max(1, user_data.get('days_since_joined', 30))
        user_daily_events = user_events / user_days
        user_login_freq = user_data.get('days_since_login', 0) / user_days if user_days > 0 else 0
        
        role = user_data.get('role', '')
        baseline = self.role_baselines.get(role, self.global_baseline)
        
        z_systems = abs(user_systems - baseline.avg_systems_accessed) / baseline.std_systems if baseline.std_systems > 0 else (3.0 if user_systems != baseline.avg_systems_accessed else 0)
        z_events = abs(user_daily_events - baseline.avg_daily_events) / baseline.std_events if baseline.std_events > 0 else (3.0 if user_daily_events != baseline.avg_daily_events else 0)
        z_login = abs(user_login_freq - baseline.avg_login_frequency) / baseline.std_login if baseline.std_login > 0 else (3.0 if user_login_freq != baseline.avg_login_frequency else 0)
        
        weights = {'systems': 0.3, 'events': 0.4, 'login': 0.3}
        deviation_score = (weights['systems'] * min(1.0, z_systems/3) + weights['events'] * min(1.0, z_events/3) + weights['login'] * min(1.0, z_login/3)) * 100
        
        deviations = []
        if z_systems > 1.5: deviations.append(f"accesses {'more' if user_systems > baseline.avg_systems_accessed else 'fewer'} systems ({user_systems} vs avg {baseline.avg_systems_accessed:.1f})")
        if z_events > 1.5: deviations.append(f"{'higher' if user_daily_events > baseline.avg_daily_events else 'lower'} daily event volume ({user_daily_events:.1f} vs avg {baseline.avg_daily_events:.1f})")
        if z_login > 1.5: deviations.append(f"{'more' if user_login_freq > baseline.avg_login_frequency else 'less'} frequent login pattern")
        
        return {
            "baseline_score": min(100, round(deviation_score)),
            "deviation_details": {
                "z_score_systems": round(z_systems, 2), 
                "z_score_events": round(z_events, 2), 
                "z_score_login": round(z_login, 2), 
                "baseline_used": role if role in self.role_baselines else "global"
            },
            "reason": f"Deviation detected: {'; '.join(deviations)}" if deviations else "Behavioral pattern matches baseline",
            "confidence": baseline.confidence
        }