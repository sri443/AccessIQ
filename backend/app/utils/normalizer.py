import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re


class DataNormalizer:
    """Handles all data normalization and cleaning operations."""
    
    @staticmethod
    def normalize_timestamps(df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Normalize timestamp columns to standard datetime format."""
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    
    @staticmethod
    def normalize_departments(df: pd.DataFrame, col: str = 'department') -> pd.DataFrame:
        """Standardize department names."""
        if col in df.columns:
            department_map = {
                'information technology': 'IT',
                'it': 'IT',
                'human resources': 'HR',
                'hr': 'HR',
                'engineering': 'Engineering',
                'eng': 'Engineering',
                'marketing': 'Marketing',
                'mktg': 'Marketing',
                'legal': 'Legal',
                'executive': 'Executive',
                'exec': 'Executive',
                'operations': 'Operations',
                'ops': 'Operations',
            }
            df[col] = df[col].str.lower().str.strip()
            df[col] = df[col].map(lambda x: department_map.get(x, x.title()))
        return df
    
    @staticmethod
    def normalize_account_types(df: pd.DataFrame, col: str = 'account_type') -> pd.DataFrame:
        """Normalize account type values."""
        if col in df.columns:
            type_map = {
                'employee': 'Employee',
                'emp': 'Employee',
                'contractor': 'Contractor',
                'ctr': 'Contractor',
                'service': 'Service',
                'svc': 'Service',
                'service_account': 'Service',
                'admin': 'Admin',
            }
            df[col] = df[col].str.lower().str.strip()
            df[col] = df[col].map(lambda x: type_map.get(x, x.title()))
        return df
    
    @staticmethod
    def normalize_privileges(df: pd.DataFrame, col: str = 'systems') -> pd.DataFrame:
        """Normalize system/privilege names."""
        if col in df.columns:
            # Convert string representation of list to actual list
            if df[col].dtype == 'object':
                df[col] = df[col].apply(
                    lambda x: [s.strip() for s in str(x).strip('[]').replace("'", "").replace('"', '').split(',')]
                    if isinstance(x, str) else x
                )
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with sensible defaults."""
        # Fill missing names
        if 'name' in df.columns:
            df['name'] = df['name'].fillna('Unknown User')
        
        # Fill missing departments
        if 'department' in df.columns:
            df['department'] = df['department'].fillna('Unassigned')
        
        # Fill missing roles
        if 'role' in df.columns:
            df['role'] = df['role'].fillna('Standard User')
        
        # Fill missing account types
        if 'account_type' in df.columns:
            df['account_type'] = df['account_type'].fillna('Employee')
        
        # Fill missing dates with current date
        date_cols = ['joined_date', 'last_login', 'created_at']
        for col in date_cols:
            if col in df.columns:
                df[col] = df[col].fillna(pd.Timestamp.now())
        
        # Fill missing systems
        if 'systems' in df.columns:
            df['systems'] = df['systems'].fillna('[]')
        
        # Fill missing owner
        if 'owner' in df.columns:
            df['owner'] = df['owner'].fillna('Unknown')
        
        return df
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """Remove duplicate records."""
        if subset is None:
            subset = ['id']
        return df.drop_duplicates(subset=subset, keep='first')
    
    @staticmethod
    def process_users_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Complete processing pipeline for users dataframe."""
        df = DataNormalizer.remove_duplicates(df)
        df = DataNormalizer.handle_missing_values(df)
        df = DataNormalizer.normalize_timestamps(df, ['joined_date', 'last_login'])
        df = DataNormalizer.normalize_departments(df)
        df = DataNormalizer.normalize_account_types(df)
        df = DataNormalizer.normalize_privileges(df)
        return df
    
    @staticmethod
    def process_events_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Complete processing pipeline for events dataframe."""
        df = DataNormalizer.remove_duplicates(df)
        df = DataNormalizer.handle_missing_values(df)
        if 'timestamp' in df.columns:
            df = DataNormalizer.normalize_timestamps(df, ['timestamp'])
        if 'user_id' in df.columns:
            df = df.dropna(subset=['user_id'])
        return df