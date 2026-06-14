from typing import Dict, Any, List, Optional
from app.services.data_processor import DataProcessor


class CrossDepartmentDetector:
    """Detects cross-department access patterns."""
    
    @classmethod
    def detect(cls, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect suspicious cross-department access.
        """
        department = user_data.get('department', '')
        user_systems = user_data.get('systems', [])
        
        # Get suspicious systems for department
        suspicious_systems = DataProcessor.get_department_boundaries(department)
        
        # Find systems that cross department boundaries
        crossed_systems = [s for s in user_systems if s in suspicious_systems]
        
        if crossed_systems:
            description = f"{department} user accessing {', '.join(crossed_systems)} outside departmental scope"
            
            return {
                'type': 'Cross-Department Access',
                'description': description,
                'points': min(25, len(crossed_systems) * 15),
                'confidence': min(1.0, len(crossed_systems) / 3),
                'details': {
                    'department': department,
                    'crossed_systems': crossed_systems
                }
            }
        
        return None