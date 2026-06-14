import pandas as pd
import os
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import aiofiles
from fastapi import UploadFile

from app.utils.normalizer import DataNormalizer

class CSVParser:
    """Handles CSV file parsing and validation."""

    REQUIRED_USER_COLUMNS = ['id', 'name', 'department', 'role', 'account_type']
    OPTIONAL_USER_COLUMNS = ['joined_date', 'last_login', 'systems', 'owner', 'privilege_level']

    REQUIRED_EVENT_COLUMNS = ['id', 'user_id', 'event_type', 'timestamp']
    OPTIONAL_EVENT_COLUMNS = ['system', 'resource', 'action', 'result']

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    async def save_upload(self, file: UploadFile, filename: str) -> str:
        """Save uploaded file to disk."""
        file_path = self.upload_dir / filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        return str(file_path)

    def validate_users_csv(self, file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Validate and parse users CSV file."""
        try:
            df = pd.read_csv(file_path)
            df=df.fillna('')

            # Check required columns
            missing_cols = [col for col in self.REQUIRED_USER_COLUMNS if col not in df.columns]
            if missing_cols:
                return False, f"Missing required columns: {', '.join(missing_cols)}", None

            # Process and clean data
            df = DataNormalizer.process_users_dataframe(df)

            # Calculate derived fields
            now = pd.Timestamp.now()
            if 'last_login' in df.columns:
                df['days_since_login'] = (now - pd.to_datetime(df['last_login'])).dt.days.fillna(0).astype(int)
            else:
                df['days_since_login'] = 0

            if 'joined_date' in df.columns:
                df['days_since_joined'] = (now - pd.to_datetime(df['joined_date'])).dt.days.fillna(0).astype(int)
            else:
                df['days_since_joined'] = 0

            return True, "CSV validated successfully", df

        except Exception as e:
            return False, f"Error parsing CSV: {str(e)}", None

    def validate_events_csv(self, file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Validate and parse events CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            # Handle column renaming
            if 'event_id' in df.columns and 'id' not in df.columns:
                df = df.rename(columns={'event_id': 'id'})

            # Check required columns
            missing_cols = [col for col in self.REQUIRED_EVENT_COLUMNS if col not in df.columns]
            if missing_cols:
                return False, f"Missing required columns: {', '.join(missing_cols)}", None

            # Process and clean data
            df = DataNormalizer.process_events_dataframe(df)

            return True, "Events CSV validated successfully", df

        except Exception as e:
            return False, f"Error parsing events CSV: {str(e)}", None

    @staticmethod
    def get_dataframe_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic statistics about the dataframe."""
        stats = {
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'null_counts': df.isnull().sum().to_dict(),
            'unique_users': df['id'].nunique() if 'id' in df.columns else 0,
        }

        if 'department' in df.columns:
            stats['departments'] = df['department'].value_counts().to_dict()

        if 'account_type' in df.columns:
            stats['account_types'] = df['account_type'].value_counts().to_dict()

        return stats