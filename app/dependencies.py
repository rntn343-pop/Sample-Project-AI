from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import User
from .security import decode_access_token, extract_token


def _resolve_current_user(request: Request, db: Session) -> User | None:
    username = None
    token = extract_token(request)
    if token:
        username = decode_access_token(token)
    if not username:
        username = request.session.get("username")
    if not username:
        return None

    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        return None

    request.session["last_activity"] = datetime_iso()
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = _resolve_current_user(request, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """Return the signed-in user when available, otherwise None.

    This is used for public pages where the navigation should still reflect
    an authenticated browser session.
    """
    return _resolve_current_user(request, db)


def datetime_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()