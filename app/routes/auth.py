from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..security import create_access_token
from ..services.auth_service import authenticate, create_user

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.data_dir.parent / "app" / "templates"))


def _login_session(request: Request, username: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    request.session.clear()
    request.session["username"] = username
    request.session["login_time"] = now
    request.session["last_activity"] = now


def _set_token(response: RedirectResponse | object, username: str) -> None:
    if hasattr(response, "set_cookie"):
        response.set_cookie(
            "access_token",
            create_access_token(username),
            httponly=True,
            samesite="lax",
            secure=settings.cookie_secure,
            max_age=settings.session_max_age_seconds,
            path="/",
        )


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"request": request, "user": None})


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    errors: list[str] = []
    if password != confirm_password:
        errors.append("Passwords do not match.")
    try:
        if not errors:
            user = create_user(db, username, email, password)
            _login_session(request, user.username)
            response = RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
            _set_token(response, user.username)
            return response
    except ValueError as exc:
        errors.append(str(exc))
    return templates.TemplateResponse(request=request, name="register.html", context={"request": request, "user": None, "errors": errors, "form": {"username": username, "email": email}})


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "user": None})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate(db, username, password)
    if user is None:
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "user": None, "error": "Invalid username or password.", "form": {"username": username}})
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    _login_session(request, user.username)
    response = RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    _set_token(response, user.username)
    return response


@router.get("/logout")
@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token", path="/")
    return response


@router.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form_data.username, form_data.password)
    if user is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}