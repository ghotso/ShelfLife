"""
Action logs API router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ActionLog
from app.schemas import ActionLogResponse

router = APIRouter()


@router.get("", response_model=list[ActionLogResponse])
def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    """Get action logs"""
    logs = db.query(ActionLog).order_by(ActionLog.created_at.desc()).limit(limit).all()
    return logs

