from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
from app.services.csv_parser import CSVParser
import pandas as pd

router = APIRouter()
csv_parser = CSVParser()

# Global state - use a mutable container to ensure persistence
class AppState:
    USER_DATA: pd.DataFrame = None
    EVENT_DATA: pd.DataFrame = None

state = AppState()

@router.post("/upload/users")
async def upload_users(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload identity_users.csv"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are supported")
    
    file_path = await csv_parser.save_upload(file, f"users_{file.filename}")
    valid, message, df = csv_parser.validate_users_csv(file_path)
    
    if not valid:
        raise HTTPException(400, message)
    
    state.USER_DATA = df
    stats = csv_parser.get_dataframe_stats(df)
    
    return {
        "status": "success",
        "message": message,
        "rows_processed": len(df),
        "stats": stats
    }


@router.post("/upload/events")
async def upload_events(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload identity_events.csv"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are supported")
    
    file_path = await csv_parser.save_upload(file, f"events_{file.filename}")
    valid, message, df = csv_parser.validate_events_csv(file_path)
    
    if not valid:
        raise HTTPException(400, message)
    
    state.EVENT_DATA = df
    stats = csv_parser.get_dataframe_stats(df)
    
    return {
        "status": "success",
        "message": message,
        "rows_processed": len(df),
        "stats": stats
    }


def get_user_data():
    return state.USER_DATA

def get_event_data():
    return state.EVENT_DATA