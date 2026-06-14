from typing import Dict, Any, List, Optional


class StaleAccountDetector:
    """Detects stale and inactive accounts."""
    
    # Staleness thresholds
    THRESHOLDS = {
        'Admin': {'days': 30, 'points': 35},
        'Contractor': {'days': 15, 'points': 30},
        'Service': {'days': 45, 'points': 25},
        'default': {'days': 90, 'points': 20},
    }
    
    @classmethod
    def detect(cls, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect stale accounts based on role and inactivity period.
        Returns finding dict if stale, None otherwise.
        """
        days_since_login = user_data.get('days_since_login', 0)
        role = user_data.get('role', '')
        account_type = user_data.get('account_type', '')
        
        # Determine threshold
        threshold_config = cls.THRESHOLDS.get(role) or cls.THRESHOLDS.get(account_type) or cls.THRESHOLDS['default']
        
        if days_since_login > threshold_config['days']:
            finding_type = 'Stale Admin' if role == 'Admin' else 'Stale Account'
            description = f"Account inactive for {days_since_login} days ({role} threshold: {threshold_config['days']} days)"
            
            return {
                'type': finding_type,
                'description': description,
                'points': threshold_config['points'],
                'confidence': min(1.0, days_since_login / (threshold_config['days'] * 2))
            }
        
        return None