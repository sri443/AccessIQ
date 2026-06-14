from typing import Dict, Any, Optional


class OrphanServiceDetector:
    """Detects orphan service accounts."""
    
    @classmethod
    def detect(cls, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect service accounts with no owner or high privileges.
        """
        account_type = user_data.get('account_type', '')
        owner = user_data.get('owner')
        privilege_level = user_data.get('privilege_level', '')
        
        # Check if it's a service account
        if account_type != 'Service':
            return None
        
        # Check for missing owner
        if not owner or owner in ['Unknown', '', 'None', 'null']:
            return {
                'type': 'Orphan Service Account',
                'description': 'Service account has no assigned owner and elevated privileges',
                'points': 40,
                'confidence': 0.95,
                'details': {
                    'account_type': account_type,
                    'owner': owner,
                    'privilege_level': privilege_level
                }
            }
        
        # Check for high privilege service accounts
        if privilege_level and privilege_level.lower() in ['high', 'admin', 'elevated']:
            return {
                'type': 'High-Privilege Service Account',
                'description': f'Service account with {privilege_level} privileges and owner: {owner}',
                'points': 20,
                'confidence': 0.7,
                'details': {
                    'account_type': account_type,
                    'owner': owner,
                    'privilege_level': privilege_level
                }
            }
        
        return None