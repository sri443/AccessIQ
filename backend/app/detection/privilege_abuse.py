from typing import Dict, Any, Optional, List
from app.services.data_processor import DataProcessor


class PrivilegeAbuseDetector:
    """Detects patterns indicative of privilege abuse."""
    
    @classmethod
    def detect(cls, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect privilege abuse patterns.
        """
        user_systems = user_data.get('systems', [])
        event_count = user_data.get('event_count', 0)
        unique_systems = user_data.get('unique_systems_accessed', len(user_systems))
        sensitive_systems = DataProcessor.get_sensitive_systems()
        
        findings = []
        
        # Check for access to multiple sensitive systems
        sensitive_accessed = [s for s in user_systems if s in sensitive_systems]
        if len(sensitive_accessed) >= 3:
            findings.append({
                'type': 'Privilege Abuse',
                'description': f'Access to {len(sensitive_accessed)} sensitive systems: {", ".join(sensitive_accessed)}',
                'points': 20,
                'confidence': min(1.0, len(sensitive_accessed) / 5),
                'details': {
                    'sensitive_systems': sensitive_accessed
                }
            })
        
        # Check for unusual access volume
        if event_count > 1000 and user_data.get('recent_events', 0) > 500:
            findings.append({
                'type': 'Unusual Access Volume',
                'description': f'High access volume: {event_count} events, {user_data.get("recent_events", 0)} recent',
                'points': 15,
                'confidence': 0.6,
                'details': {
                    'event_count': event_count,
                    'recent_events': user_data.get('recent_events', 0)
                }
            })
        
        # Return combined finding if any
        if findings:
            combined_description = '; '.join([f['description'] for f in findings])
            combined_points = sum([f['points'] for f in findings])
            return {
                'type': 'Privilege Abuse Pattern',
                'description': combined_description,
                'points': min(30, combined_points),
                'confidence': max([f['confidence'] for f in findings]),
                'details': findings
            }
        
        return None