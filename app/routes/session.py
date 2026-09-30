from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import SessionDataUpdate

router = APIRouter()


@router.get("/session-info")
async def session_info(request: Request, user: User = Depends(get_current_user)):
    login_time = request.session.get("login_time")
    last_activity = request.session.get("last_activity")
    return {
        "username": user.username,
        "login_active": bool(login_time),
        "session_id_present": bool(request.session.get("username")),
        "login_time": login_time,
        "last_activity": last_activity,
        "session_data": user.session_data or {},
    }


@router.post("/session-data")
async def update_session_data(payload: SessionDataUpdate, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.session_data = {**(user.session_data or {}), **payload.data}
    request.session["last_activity"] = datetime.now(timezone.utc).isoformat()
    db.commit()
    return {"message": "Session data updated", "data": user.session_data}