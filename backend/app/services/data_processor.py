import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict


class DataProcessor:
    """Processes and enriches user data for analysis."""
    
    # Role baseline permissions
    ROLE_BASELINES = {
        'Finance Analyst': ['ERP', 'FinanceDB'],
        'HR Manager': ['HRDB', 'Payroll', 'ERP'],
        'DevOps Engineer': ['AWS', 'GitHub', 'CI/CD'],
        'Admin': ['AWS', 'AzureAD', 'ERP', 'HRDB', 'FinanceDB', 'Payroll', 'GitHub', 'CI/CD'],
        'CTO': ['AWS', 'AzureAD', 'ERP', 'HRDB', 'FinanceDB', 'Payroll', 'GitHub', 'CI/CD'],
        'Software Engineer': ['GitHub', 'CI/CD', 'AWS'],
        'Database Admin': ['FinanceDB', 'HRDB', 'AWS'],
        'Security Analyst': ['AWS', 'AzureAD', 'SIEM'],
        'Standard User': ['ERP'],
    }
    
    # Sensitive systems
    SENSITIVE_SYSTEMS = ['AWS', 'FinanceDB', 'HRDB', 'Payroll', 'AzureAD']
    
    # Department boundaries for cross-department detection
    DEPARTMENT_BOUNDARIES = {
        'Finance': ['HRDB', 'GitHub', 'CI/CD'],
        'HR': ['FinanceDB', 'AWS', 'CI/CD'],
        'Marketing': ['FinanceDB', 'HRDB', 'GitHub'],
        'Engineering': ['FinanceDB', 'Payroll', 'HRDB'],
    }
    
    @classmethod
    def get_expected_systems(cls, role: str) -> List[str]:
        """Get expected systems for a given role."""
        return cls.ROLE_BASELINES.get(role, ['ERP'])
    
    @classmethod
    def get_sensitive_systems(cls) -> List[str]:
        """Get list of sensitive systems."""
        return cls.SENSITIVE_SYSTEMS
    
    @classmethod
    def get_department_boundaries(cls, department: str) -> List[str]:
        """Get systems that would be suspicious for a department."""
        return cls.DEPARTMENT_BOUNDARIES.get(department, [])
    
    @staticmethod
    def parse_systems(systems_value) -> List[str]:
        """Parse systems field into list."""
        if isinstance(systems_value, list):
            return systems_value
        if isinstance(systems_value, str):
            # Try parsing as string list
            cleaned = systems_value.strip('[]').replace("'", "").replace('"', '')
            return [s.strip() for s in cleaned.split(',') if s.strip()]
        return []
    
    @classmethod
    def enrich_user_data(cls, users_df: pd.DataFrame, events_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """Enrich user data with computed fields."""
        enriched_users = []
        
        for _, row in users_df.iterrows():
            user_data = {
                'id': row.get('id', ''),
                'name': row.get('name', 'Unknown'),
                'department': row.get('department', 'Unassigned'),
                'role': row.get('role', 'Standard User'),
                'account_type': row.get('account_type', 'Employee'),
                'joined_date': str(row.get('joined_date', '')),
                'last_login': str(row.get('last_login', '')),
                'systems': cls.parse_systems(row.get('systems', [])),
                'owner': row.get('owner', 'Self' if row.get('account_type') != 'Service' else None),
                'privilege_level': row.get('privilege_level', 'standard'),
                'days_since_login': int(row.get('days_since_login', 0)),
                'days_since_joined': int(row.get('days_since_joined', 0)),
            }
            
            # Add event data if available
            if events_df is not None:
                user_events = events_df[events_df['user_id'] == user_data['id']]
                user_data['event_count'] = len(user_events)
                user_data['unique_systems_accessed'] = user_events['system'].nunique() if 'system' in user_events.columns else 0
                user_data['recent_events'] = len(user_events[user_events['timestamp'] > pd.Timestamp.now() - pd.Timedelta(days=30)])
            else:
                user_data['event_count'] = 0
                user_data['unique_systems_accessed'] = len(user_data['systems'])
                user_data['recent_events'] = 0
            
            enriched_users.append(user_data)
        
        return enriched_users