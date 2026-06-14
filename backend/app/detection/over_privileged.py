from typing import Dict, Any, List, Optional
from app.services.data_processor import DataProcessor


class OverPrivilegedDetector:
    """Detects over-privileged users based on role baselines."""
    
    @classmethod
    def detect(cls, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect excessive permissions beyond role baseline.
        """
        role = user_data.get('role', '')
        user_systems = user_data.get('systems', [])
        
        # Get expected systems for role
        expected_systems = DataProcessor.get_expected_systems(role)
        
        # Find unexpected systems
        unexpected_systems = [s for s in user_systems if s not in expected_systems]
        
        if unexpected_systems:
            description = f"User has access to {len(unexpected_systems)} systems beyond role baseline: {', '.join(unexpected_systems)}"
            
            return {
                'type': 'Over-Privileged',
                'description': description,
                'points': min(30, len(unexpected_systems) * 10),  # Scale with number of extra systems
                'confidence': min(1.0, len(unexpected_systems) / 5),
                'details': {
                    'expected_systems': expected_systems,
                    'unexpected_systems': unexpected_systems
                }
            }
        
        return None