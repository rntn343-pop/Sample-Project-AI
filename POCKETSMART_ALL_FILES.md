# PocketSmart AI — Complete Source Files

Every section below is the complete contents of the corresponding text source/configuration file.

## `.env.example`

```bash
APP_NAME=PocketSmart AI
SECRET_KEY=replace-this-with-a-long-random-secret
DATABASE_URL=sqlite:///./data/pocketsmart.db

# Gemini configuration
GEMINI_API_KEY=

# Choose one Gemini model. The following are current Gemini API examples.
#
# Latest:
#   gemini-3.8-flash
#
# Additional:
#   gemini-3.7-flash
#   gemini-3.6-flash
#   gemini-3.5-flash
#   gemini-3.5-flash-lite
#   gemini-3.1-flash-lite
#   gemini-2.5-flash
#   gemini-2.5-flash-lite
#
# GEMINI_MODEL controls the model used by PocketSmart.
GEMINI_MODEL=gemini-3.8-flash

GEMINI_TEMPERATURE=0.4
GEMINI_MAX_OUTPUT_TOKENS=4500
GEMINI_DEBUG=true
GEMINI_FALLBACK_ON_ERROR=false

SESSION_MAX_AGE_SECONDS=1800
MAX_UPLOAD_MB=5
COOKIE_SECURE=false
CORS_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

## `.gitignore`

```text
.venv/
__pycache__/
.pytest_cache/
*.py[cod]
.env
*.db
*.sqlite
uploads/*
!uploads/.gitkeep
data/*
!data/.gitkeep
.DS_Store
.vscode/
```

## `.pytest_cache/.gitignore`

```text
# Created by pytest automatically.
*
```

## `.pytest_cache/CACHEDIR.TAG`

```text
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html
```

## `.pytest_cache/README.md`

```markdown
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.
```

## `.pytest_cache/v/cache/nodeids`

```text
[
  "tests/test_auth.py::test_register_login_and_protected_page",
  "tests/test_auth.py::test_token_endpoint",
  "tests/test_brand_navigation.py::test_logo_points_to_dashboard_when_authenticated",
  "tests/test_gemini_budget.py::test_gemini_budget_is_normalized_to_user_budget",
  "tests/test_gemini_budget.py::test_gemini_compact_json_is_normalized_instead_of_rejected",
  "tests/test_gemini_budget.py::test_gemini_malformed_json_with_trailing_comma_can_be_repaired",
  "tests/test_gemini_budget.py::test_gemini_minimal_json_gets_safe_defaults",
  "tests/test_gemini_budget.py::test_safe_json_handles_code_fence",
  "tests/test_gemini_budget.py::test_safe_json_repairs_unquoted_keys_and_trailing_commas",
  "tests/test_gemini_budget.py::test_string_outfit_analysis_is_normalized_to_notes",
  "tests/test_health.py::test_health",
  "tests/test_planners.py::test_home_planner_fallback",
  "tests/test_planners.py::test_jewelry_image_upload_is_accepted",
  "tests/test_planners.py::test_jewelry_invalid_image_is_rejected",
  "tests/test_planners.py::test_jewelry_planner_fallback_without_image",
  "tests/test_planners.py::test_party_planner_fallback",
  "tests/test_session_and_history.py::test_session_info_and_history"
]
```

## `.vscode/launch.json`

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "PocketSmart API",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
      "jinja": true,
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-q"],
      "console": "integratedTerminal"
    }
  ]
}
```

## `.vscode/settings.json`

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
```

## `Dockerfile`

```text
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data uploads

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## `POCKETSMART_ALL_FILES.md`

```markdown

```

## `POCKETSMART_GEMINI_TROUBLESHOOTING.md`

```markdown
# PocketSmart AI — Gemini troubleshooting fix

The original implementation intentionally converted every Gemini exception into a local fallback result. That made configuration/API/model errors look like a missing API key.

This version changes that behavior:

- No `GEMINI_API_KEY` -> local fallback is allowed.
- `GEMINI_API_KEY` is present -> actual Gemini errors are raised and returned to the frontend as HTTP 502 with the real error message.
- Set `GEMINI_FALLBACK_ON_ERROR=true` only when you deliberately want silent local fallback after a Gemini failure.
- `python scripts/diagnose_gemini.py` verifies `.env`, model, SDK and performs a real text request.

## Windows commands

From `D:\scratch\PocketSmartAI`:

```powershell
.venv\Scripts\activate
python -m pip install -U google-genai python-dotenv
python -c "from app.config import settings; print('GEMINI_API_KEY loaded:', bool(settings.gemini_api_key)); print('GEMINI_MODEL:', settings.gemini_model)"
python scripts\diagnose_gemini.py
```

Expected configuration output is similar to:

```text
.env exists  : True
API key      : abcde...1234
Model        : gemini-3.8-flash
```

Then:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/health
```

You want:

```json
{
  "gemini_configured": true,
  "model": "gemini-3.8-flash"
}
```

## Important model setting

Do not put the old documentation value `gemini-1.5-flash-pro` in `.env`. Gemini 1.5 models were shut down by Google in September 2025. Use a currently available model such as:

```env
GEMINI_MODEL=gemini-3.8-flash
```

## If the diagnostic script fails

The script prints the exact class and API error instead of hiding it. Typical categories are:

- `.env exists: False` or `API key: NOT SET` -> `.env` location/name problem.
- `google-genai is not installed` -> wrong virtual environment or package not installed.
- `401/403` -> API key/project/access problem.
- `404` or model-not-found -> wrong/retired model name.
- `429` -> quota/rate-limit issue.
- network/timeout error -> local network, proxy or firewall problem.

Never paste the full API key into chat or screenshots.
```

## `README.md`

```markdown
# PocketSmart AI

PocketSmart AI is a complete FastAPI + Jinja2 web application for budget-aware recommendations across:

- Home interior planning
- Party planning
- Jewelry planning with optional outfit-image analysis

The implementation follows the uploaded project documentation's architecture and route inventory, while resolving its Flask/FastAPI inconsistency in favor of FastAPI because the later milestones and conclusion explicitly specify FastAPI, Jinja2, and Uvicorn.

## What is included

- FastAPI backend with modular routes/services/models
- JWT authentication plus browser session cookies
- SQLite persistence for users and recommendation history
- Gemini multimodal integration via Google's current `google-genai` SDK
- Safe deterministic fallback recommendations when no API key is configured or Gemini fails
- Search links for Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO and generic platforms
- Responsive HTML/CSS/JavaScript frontend
- Planner pages, recommendation details, history, dashboard, registration and login
- Automated tests
- Docker support

## Important model compatibility note

The source documentation names **Gemini 1.5 Flash Pro**. That model family is no longer available in the Gemini API; Google's release notes state that Gemini 1.5 models were shut down in September 2025. This project therefore defaults to `gemini-3.8-flash` and keeps the model configurable through `GEMINI_MODEL`.

Set `GEMINI_MODEL` to another model available to your account when needed. The `.env.example` file lists several current model IDs as examples. The launcher also exposes them with `python launch.py --list-models` and allows a one-time override with `python launch.py --model <MODEL_ID>`. Model availability can vary by account/project, so verify access against Google\'s current model catalog.

## Gemini troubleshooting

Run `python scripts/diagnose_gemini.py` from the activated virtual environment to verify that `.env` is being loaded, the SDK is installed, the configured model is reachable, and an actual Gemini request succeeds. When a key is configured, Gemini errors are no longer silently converted to a fallback response; the frontend reports the API error instead.

Use `GEMINI_MODEL=gemini-3.8-flash`. The Gemini 1.5 models named in the original project documentation were shut down in September 2025.

## One-click-style installer and launcher

The project includes cross-platform Python scripts so Windows, macOS, and Linux users can install and launch PocketSmart without manually activating the virtual environment.

### Install

From the project folder:

```bash
python install.py
```

The installer creates `.venv`, installs `requirements.txt`, creates/updates `.env`, and prompts for the Gemini API key. It also generates a secure `SECRET_KEY` automatically. Leave the API-key prompt blank to keep an existing key or run with the local fallback.

### Launch

```bash
python launch.py
```

The launcher uses the project virtual environment, starts Uvicorn on `http://127.0.0.1:8000`, waits for `/health`, opens the default web browser automatically, and keeps the terminal open while the server is running. Press `Ctrl+C` to stop the server.

You may change the launch host/port for a local run with:

```text
POCKETSMART_HOST=127.0.0.1
POCKETSMART_PORT=8000
```

On Windows PowerShell, for example:

```powershell
$env:POCKETSMART_PORT=8080
python launch.py
```

On macOS/Linux:

```bash
POCKETSMART_PORT=8080 python3 launch.py
```

## Quick start in VS Code

### 1. Open the folder

Open `pocketsmart_ai` in VS Code.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
```

macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` to `.env`.

Set a strong `SECRET_KEY`.

For Gemini-powered responses set:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

The application still runs without a Gemini key by using its local fallback recommendation engine.

### 5. Run the app

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000

### 6. Test

```bash
pytest -q
```

## Main routes

Browser pages:

- `/` — landing page
- `/register` — registration
- `/login` — login
- `/logout` — logout
- `/dashboard` — logged-in dashboard
- `/home-planner` — home planner
- `/party-planner` — party planner
- `/jewelry-planner` — jewelry planner
- `/history` — recommendation history
- `/recommendations-details/{id}` — recommendation detail
- `/testimonials` — demo testimonials page

API/form routes:

- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry`
- `POST /home-budget` (alias)
- `POST /party-budget` (alias)
- `POST /jewelry-budget` (alias)
- `POST /token` — JWT token using OAuth2 password form
- `GET /session-info`
- `POST /session-data`
- `GET /recommendations-details/{id}` or `GET /recommendations-details?recommendation_id={id}`
- `GET /history`
- `GET /startup`
- `GET /health`

## Product and service links

The uploaded documentation asks for third-party platform sourcing and also explicitly allows mock/simulated sourcing. This implementation does not scrape marketplaces. Gemini returns search terms and the backend creates links on known platform domains. Prices returned by Gemini are treated as estimates, not verified live marketplace prices.

## Production notes

- Replace SQLite with PostgreSQL for multi-instance deployment.
- Set `COOKIE_SECURE=true` behind HTTPS.
- Restrict `CORS_ORIGINS` to trusted origins.
- Add a real product-search provider before presenting any price as live/verified.
- Replace the demo testimonial content before production use.


### Gemini response normalization
Gemini can occasionally return valid JSON with a compact or slightly inconsistent shape, such as a string `outfit_analysis` or JSON with a trailing comma. PocketSmart normalizes those responses locally before Pydantic validation, so useful model output is preserved instead of being rejected.

The parser also repairs common JSON formatting mistakes using only the Python standard library; there is no extra JSON-repair service or API dependency.

### Budget enforcement
Gemini output is never allowed to exceed the budget submitted by the user. PocketSmart treats the submitted budget as authoritative, recalculates all line-item totals locally, reduces quantities when necessary, and removes unaffordable items rather than fabricating cheaper prices.


### Gemini model selection during installation

The installer shows these examples at the model prompt:

```text
Latest     - gemini-3.8-flash
Additional - gemini-3.7-flash
             gemini-3.6-flash
             gemini-3.5-flash
             gemini-3.5-flash-lite
             gemini-3.1-flash-lite
             gemini-2.5-flash
             gemini-2.5-flash-lite
```

Enter any model ID supported by your Gemini API key. Leaving the prompt blank keeps the existing configured model.
```

## `app/__init__.py`

```python
__all__ = ["main"]
```

## `app/config.py`

```python
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE, override=True)


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)).strip())
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "PocketSmart AI")
    secret_key: str = os.getenv("SECRET_KEY", "dev-only-secret-change-me-please-32-bytes-minimum")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/pocketsmart.db")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    gemini_temperature: float = _float_env("GEMINI_TEMPERATURE", 0.4)
    gemini_max_output_tokens: int = _int_env("GEMINI_MAX_OUTPUT_TOKENS", 4500)
    gemini_debug: bool = _bool_env("GEMINI_DEBUG", False)
    gemini_fallback_on_error: bool = _bool_env("GEMINI_FALLBACK_ON_ERROR", False)
    session_max_age_seconds: int = _int_env("SESSION_MAX_AGE_SECONDS", 1800)
    max_upload_mb: int = _int_env("MAX_UPLOAD_MB", 5)
    cookie_secure: bool = _bool_env("COOKIE_SECURE", False)
    cors_origins: tuple[str, ...] = tuple(
        _csv(
            os.getenv(
                "CORS_ORIGINS",
                "http://127.0.0.1:8000,http://localhost:8000",
            )
        )
    )
    upload_dir: Path = BASE_DIR / "uploads"
    data_dir: Path = BASE_DIR / "data"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)
```

## `app/db.py`

```python
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
```

## `app/dependencies.py`

```python
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
```

## `app/main.py`

```python
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from .config import settings
from .db import init_db
from .routes import auth, pages, planners, session


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins) if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=settings.session_max_age_seconds,
    same_site="lax",
    https_only=settings.cookie_secure,
)

app.mount("/static", StaticFiles(directory=str(settings.data_dir.parent / "app" / "static")), name="static")

app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(planners.router)
app.include_router(session.router)

templates = Jinja2Templates(directory=str(settings.data_dir.parent / "app" / "templates"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name, "gemini_configured": bool(settings.gemini_api_key), "model": settings.gemini_model}


@app.get("/startup")
async def startup_status():
    return {"status": "initialized", "database": settings.database_url, "gemini_configured": bool(settings.gemini_api_key)}


@app.exception_handler(404)
async def not_found(request: Request, exc):
    if request.url.path.startswith("/generate-") or request.url.path.startswith("/session-") or request.url.path.startswith("/api/"):
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return templates.TemplateResponse(request=request, name="404.html", context={"request": request, "user": None}, status_code=404)


@app.get("/docs-info", include_in_schema=False)
async def docs_info():
    return {"message": "FastAPI Swagger docs are available at /docs and ReDoc at /redoc."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
```

## `app/models.py`

```python
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    session_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", order_by="Recommendation.created_at.desc()"
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recommendation_type: Mapped[str] = mapped_column(String(30), index=True)
    input_data: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict] = mapped_column(JSON)
    result_summary: Mapped[str] = mapped_column(Text)
    image_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    user: Mapped[User] = relationship(back_populates="recommendations")
```

## `app/routes/__init__.py`

```python

```

## `app/routes/auth.py`

```python
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
```

## `app/routes/pages.py`

```python
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..dependencies import get_current_user, get_optional_current_user
from ..models import User
from ..services.history_service import get_recommendation, list_recommendations

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.data_dir.parent / "app" / "templates"))


@router.get("/")
async def index(
    request: Request,
    user: User | None = Depends(get_optional_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "user": user},
    )


@router.get("/testimonials")
async def testimonials(
    request: Request,
    user: User | None = Depends(get_optional_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="testimonials.html",
        context={"request": request, "user": user},
    )


@router.get("/dashboard")
async def dashboard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = list_recommendations(db, user.id, 5)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"request": request, "user": user, "history": history})


@router.get("/history")
async def history(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = list_recommendations(db, user.id, 50)
    return templates.TemplateResponse(request=request, name="history.html", context={"request": request, "user": user, "history": rows})


@router.get("/history/{recommendation_id}")
async def history_detail(request: Request, recommendation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = get_recommendation(db, user.id, recommendation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    template_name = {
        "home": "home_recommendations.html",
        "party": "party_recommendations.html",
        "jewelry": "jewelry_recommendations.html",
    }.get(row.recommendation_type, "recommendations_details.html")
    return templates.TemplateResponse(request=request, name=template_name, context={"request": request, "user": user, "recommendation": row})


@router.get("/recommendations-details")
async def recommendation_detail_query(request: Request, recommendation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await history_detail(request, recommendation_id, user, db)


@router.get("/recommendations-details/{recommendation_id}")
async def recommendation_detail(request: Request, recommendation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await history_detail(request, recommendation_id, user, db)


@router.get("/home-planner")
async def home_planner(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="home_planner.html", context={"request": request, "user": user})


@router.get("/party-planner")
async def party_planner(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="party_planner.html", context={"request": request, "user": user})


@router.get("/jewelry-planner")
async def jewelry_planner(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="jewelry_planner.html", context={"request": request, "user": user})
```

## `app/routes/planners.py`

```python
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import HomeBudgetInput, JewelryBudgetInput, PartyBudgetInput
from ..services.fallback import home_fallback, jewelry_fallback, party_fallback
from ..services.gemini_utils import (
    GeminiIntegrationError,
    generate_home_recommendations,
    generate_jewelry_recommendations,
    generate_party_recommendations,
)
from ..services.history_service import save_recommendation
from ..services.image_service import validate_image

router = APIRouter()


def wants_json(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "application/json" in accept or request.headers.get("x-requested-with") == "XMLHttpRequest"


def _persist(db: Session, user: User, kind: str, input_data: dict, result: dict, image_filename: str | None = None):
    row = save_recommendation(db, user.id, kind, input_data, result, image_filename=image_filename)
    return row


def _response(request: Request, row):
    payload = {
        "id": row.id,
        "type": row.recommendation_type,
        "result": row.result,
        "details_url": f"/recommendations-details/{row.id}",
        "created_at": row.created_at.isoformat() if row.created_at else datetime.now(timezone.utc).isoformat(),
    }
    if wants_json(request):
        return JSONResponse(payload)
    return RedirectResponse(payload["details_url"], status_code=303)


@router.post("/generate-home")
@router.post("/home-budget")
async def generate_home(
    request: Request,
    total_budget: float = Form(...),
    num_lights: int = Form(0),
    num_fans: int = Form(0),
    num_furniture: int = Form(0),
    num_dining_tables: int = Form(0),
    rooms: list[str] = Form(default=[]),
    additional_requirements: str = Form(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = HomeBudgetInput(
            total_budget=total_budget,
            num_lights=num_lights,
            num_fans=num_fans,
            num_furniture=num_furniture,
            num_dining_tables=num_dining_tables,
            rooms=rooms,
            additional_requirements=additional_requirements,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        result = generate_home_recommendations(data.model_dump())
    except GeminiIntegrationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    row = _persist(db, user, "home", data.model_dump(), result)
    user.session_data = {**(user.session_data or {}), "last_home_budget": data.model_dump(), "last_recommendation_id": row.id}
    db.commit()
    return _response(request, row)


@router.post("/generate-party")
@router.post("/party-budget")
async def generate_party(
    request: Request,
    total_budget: float = Form(...),
    num_guests: int = Form(...),
    party_type: str = Form(...),
    venue_type: str = Form(...),
    needs_catering: bool = Form(False),
    needs_decoration: bool = Form(False),
    needs_entertainment: bool = Form(False),
    additional_requirements: str = Form(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = PartyBudgetInput(
            total_budget=total_budget,
            num_guests=num_guests,
            party_type=party_type,
            venue_type=venue_type,
            needs_catering=needs_catering,
            needs_decoration=needs_decoration,
            needs_entertainment=needs_entertainment,
            additional_requirements=additional_requirements,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        result = generate_party_recommendations(data.model_dump())
    except GeminiIntegrationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    row = _persist(db, user, "party", data.model_dump(), result)
    user.session_data = {**(user.session_data or {}), "last_party_budget": data.model_dump(), "last_recommendation_id": row.id}
    db.commit()
    return _response(request, row)


@router.post("/generate-jewelry")
@router.post("/jewelry-budget")
async def generate_jewelry(
    request: Request,
    total_budget: float = Form(...),
    occasion: str = Form(...),
    preferences: str = Form(""),
    image: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = JewelryBudgetInput(total_budget=total_budget, occasion=occasion, preferences=preferences)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    image_bytes = None
    image_filename = None
    mime = None
    if image and image.filename:
        image_bytes = await image.read()
        mime = image.content_type or ""
        try:
            validate_image(image_bytes, mime, settings.max_upload_mb * 1024 * 1024)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        suffix = Path(image.filename).suffix.lower() or ".img"
        image_filename = f"{uuid4().hex}{suffix}"
        (settings.upload_dir / image_filename).write_bytes(image_bytes)

    try:
        result = generate_jewelry_recommendations(data.model_dump(), image_bytes, mime)
    except GeminiIntegrationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    row = _persist(db, user, "jewelry", data.model_dump(), result, image_filename=image_filename)
    user.session_data = {
        **(user.session_data or {}),
        "last_jewelry_budget": {**data.model_dump(), "has_image": bool(image_filename)},
        "last_recommendation_id": row.id,
    }
    db.commit()
    return _response(request, row)
```

## `app/routes/session.py`

```python
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
```

## `app/schemas.py`

```python
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class HomeBudgetInput(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    num_lights: int = Field(ge=0, le=100)
    num_fans: int = Field(ge=0, le=100)
    num_furniture: int = Field(ge=0, le=100)
    num_dining_tables: int = Field(ge=0, le=50)
    rooms: list[str] = Field(default_factory=list, max_length=10)
    additional_requirements: str = Field(default="", max_length=2000)

    @field_validator("rooms")
    @classmethod
    def clean_rooms(cls, value: list[str]) -> list[str]:
        allowed = {"Living Room", "Kitchen", "Bedroom", "Dining Room", "Balcony", "Home Office"}
        return [room for room in value if room in allowed]


class PartyBudgetInput(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    num_guests: int = Field(gt=0, le=10000)
    party_type: str = Field(min_length=2, max_length=80)
    venue_type: str = Field(min_length=2, max_length=80)
    needs_catering: bool = False
    needs_decoration: bool = False
    needs_entertainment: bool = False
    additional_requirements: str = Field(default="", max_length=2000)


class JewelryBudgetInput(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=100)
    preferences: str = Field(default="", max_length=2000)


class ItemRecommendation(BaseModel):
    name: str
    description: str
    estimated_price: float = Field(ge=0)
    quantity: int = Field(ge=1, le=100)
    platform: str
    search_terms: str
    shopping_links: dict[str, str] = Field(default_factory=dict)


class BudgetBreakdown(BaseModel):
    category: str
    allocation: float = Field(ge=0)
    percentage_of_budget: float = Field(ge=0, le=100)
    items: list[ItemRecommendation] = Field(default_factory=list)


class OutfitAnalysis(BaseModel):
    dominant_colors: list[str] = Field(default_factory=list)
    style: str = ""
    formality: str = ""
    notes: str = ""


class RecommendationResponse(BaseModel):
    total_budget: float = Field(ge=0)
    allocated_budget: float = Field(ge=0)
    remaining_budget: float
    overview: str
    budget_breakdown: list[BudgetBreakdown]
    outfit_analysis: OutfitAnalysis | None = None
    styling_tips: list[str] = Field(default_factory=list)
    additional_suggestions: list[str] = Field(default_factory=list)
    source: str = "gemini"
    warnings: list[str] = Field(default_factory=list)


class SessionDataUpdate(BaseModel):
    data: dict[str, Any]
```

## `app/security.py`

```python
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Request

from .config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, salt_b64, digest_b64 = encoded.split("$", 2)
        if scheme != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(username: str, minutes: int | None = None) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.session_max_age_seconds / 60)
    payload = {"sub": username, "exp": expiry, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        return str(subject) if subject else None
    except jwt.PyJWTError:
        return None


def extract_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    cookie = request.cookies.get("access_token")
    return cookie


def is_valid_username(username: str) -> bool:
    if not 3 <= len(username) <= 50:
        return False
    return all(ch.isalnum() or ch in "._-" for ch in username)
```

## `app/services/__init__.py`

```python

```

## `app/services/auth_service.py`

```python
from __future__ import annotations

import re
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User
from ..security import hash_password, is_valid_username, verify_password

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def create_user(db: Session, username: str, email: str, password: str) -> User:
    username = username.strip()
    email = email.strip().lower()
    if not is_valid_username(username):
        raise ValueError("Username must be 3-50 characters and contain only letters, numbers, '.', '_' or '-'.")
    if not EMAIL_RE.match(email):
        raise ValueError("Enter a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    existing_username = db.scalar(select(User).where(User.username == username))
    if existing_username:
        raise ValueError("Username is already registered.")
    existing_email = db.scalar(select(User).where(User.email == email))
    if existing_email:
        raise ValueError("Email is already registered.")
    user = User(username=username, email=email, password_hash=hash_password(password), session_data={})
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.username == username.strip()))
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
```

## `app/services/catalog.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class Platform:
    name: str
    template: str


PLATFORMS = {
    "amazon": Platform("Amazon", "https://www.amazon.in/s?k={q}"),
    "flipkart": Platform("Flipkart", "https://www.flipkart.com/search?q={q}"),
    "ikea": Platform("IKEA", "https://www.ikea.com/in/en/search/?q={q}"),
    "swiggy": Platform("Swiggy", "https://www.swiggy.com/search?query={q}"),
    "zomato": Platform("Zomato", "https://www.zomato.com/search?q={q}"),
    "oyo": Platform("OYO", "https://www.oyorooms.com/search/?q={q}"),
    "myntra": Platform("Myntra", "https://www.myntra.com/{q}"),
    "google": Platform("Google", "https://www.google.com/search?q={q}"),
}

CATEGORY_PLATFORMS = {
    "lighting": ["amazon", "ikea"],
    "fans": ["amazon", "flipkart"],
    "furniture": ["ikea", "amazon", "flipkart"],
    "dining": ["ikea", "amazon", "flipkart"],
    "venue": ["google", "oyo"],
    "catering": ["swiggy", "zomato"],
    "decoration": ["amazon", "flipkart", "myntra"],
    "entertainment": ["google", "amazon"],
    "jewelry": ["amazon", "flipkart", "myntra"],
}


def build_search_links(platform_keys: list[str], search_terms: str) -> dict[str, str]:
    q = quote_plus(search_terms.strip() or "pocketsmart recommendations")
    links: dict[str, str] = {}
    for key in platform_keys:
        if key in PLATFORMS:
            links[PLATFORMS[key].name] = PLATFORMS[key].template.format(q=q)
    return links


def platform_keys_for_category(category: str) -> list[str]:
    normalized = category.strip().lower()
    for key, platforms in CATEGORY_PLATFORMS.items():
        if key in normalized or normalized in key:
            return platforms
    return ["amazon", "flipkart"]
```

## `app/services/fallback.py`

```python
from __future__ import annotations

from typing import Iterable

from .catalog import build_search_links, platform_keys_for_category


HOME_ITEMS = [
    ("Lighting", "LED ceiling light", "Energy-efficient ceiling light suitable for general room illumination.", 900),
    ("Fans", "1200 mm ceiling fan", "Standard-size ceiling fan for everyday air circulation.", 2400),
    ("Furniture", "Compact 3-seater sofa", "Budget-friendly sofa sized for a living room.", 9000),
    ("Dining", "4-seater dining table", "Compact dining table suited to small spaces.", 6500),
]

PARTY_ITEMS = [
    ("Venue", "Small event venue", "A compact venue option sized around the requested guest count.", 12000),
    ("Catering", "Indian party catering package", "Simple per-person menu package; verify menu and final rate with the provider.", 8000),
    ("Decoration", "Balloon and backdrop package", "Basic entrance/backdrop decoration package.", 4500),
    ("Entertainment", "Speaker and playlist setup", "Simple sound setup for a small event.", 3000),
]

JEWELRY_ITEMS = [
    ("Jewelry", "Minimal pendant necklace", "Versatile necklace that pairs with both traditional and modern outfits.", 1200),
    ("Jewelry", "Classic stud earrings", "Simple earrings for a clean, polished look.", 850),
    ("Jewelry", "Slim bracelet", "Minimal bracelet with a lightweight profile.", 950),
]


def _pick_items(pool: Iterable[tuple[str, str, str, float]], budget: float, max_items: int = 4) -> list[dict]:
    selected: list[dict] = []
    running = 0.0
    for category, name, description, price in pool:
        if running + price <= budget or not selected:
            quantity = 1
            selected.append(
                {
                    "category": category,
                    "name": name,
                    "description": description,
                    "estimated_price": price,
                    "quantity": quantity,
                    "platform": platform_keys_for_category(category)[0].title(),
                    "search_terms": name,
                    "shopping_links": build_search_links(platform_keys_for_category(category), name),
                }
            )
            running += price
        if len(selected) >= max_items:
            break
    return selected


def home_fallback(total_budget: float) -> dict:
    items = _pick_items(HOME_ITEMS, total_budget)
    return _build_result(total_budget, items, "fallback", "Starter home plan generated locally because Gemini was not available.")


def party_fallback(total_budget: float) -> dict:
    items = _pick_items(PARTY_ITEMS, total_budget)
    return _build_result(total_budget, items, "fallback", "Starter party plan generated locally because Gemini was not available.")


def jewelry_fallback(total_budget: float) -> dict:
    items = _pick_items(JEWELRY_ITEMS, total_budget)
    result = _build_result(total_budget, items, "fallback", "Starter jewelry plan generated locally because Gemini was not available.")
    result["outfit_analysis"] = {
        "dominant_colors": [],
        "style": "Not analyzed",
        "formality": "Not analyzed",
        "notes": "Upload an outfit image with a configured Gemini API key for multimodal color/style analysis.",
    }
    result["styling_tips"] = [
        "Keep one statement piece and make the remaining pieces simpler.",
        "Match metal tone with the outfit hardware where practical.",
        "Check final size, material and seller details before purchase.",
    ]
    return result


def _build_result(total_budget: float, items: list[dict], source: str, overview: str) -> dict:
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(item["category"], []).append(item)
    breakdown = []
    allocated = 0.0
    for category, category_items in grouped.items():
        allocation = sum(i["estimated_price"] * i["quantity"] for i in category_items)
        allocated += allocation
        breakdown.append(
            {
                "category": category,
                "allocation": round(allocation, 2),
                "percentage_of_budget": round((allocation / total_budget) * 100, 2) if total_budget else 0,
                "items": category_items,
            }
        )
    return {
        "total_budget": round(total_budget, 2),
        "allocated_budget": round(allocated, 2),
        "remaining_budget": round(total_budget - allocated, 2),
        "overview": overview,
        "budget_breakdown": breakdown,
        "outfit_analysis": None,
        "styling_tips": [],
        "additional_suggestions": [
            "Treat displayed prices as estimates unless connected to a verified product feed.",
            "Open platform links to confirm current price, availability, seller and delivery details.",
        ],
        "source": source,
        "warnings": ["Fallback recommendations are not live marketplace data."],
    }
```

## `app/services/gemini_utils.py`

```python
from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError

from ..config import settings
from ..schemas import OutfitAnalysis, RecommendationResponse
from .catalog import build_search_links, platform_keys_for_category
from .fallback import home_fallback, jewelry_fallback, party_fallback

logger = logging.getLogger("pocketsmart.gemini")


SYSTEM_INSTRUCTION = """
You are PocketSmart AI, a budget-aware recommendation assistant for users in India.
Generate practical planning recommendations. Never claim live prices or inventory unless
those values are supplied by a trusted data source. The submitted user budget is authoritative. The sum of every item estimated_price * quantity must never exceed that budget.
Never increase the user budget. If necessary, choose fewer or cheaper items. Use Indian Rupees (INR).

Return JSON that conforms to the supplied response schema. Use platform names and search
terms only; the application will generate shopping links. Do not invent direct URLs.
""".strip()


class GeminiIntegrationError(RuntimeError):
    """Raised when Gemini is configured but the API request cannot be completed."""


# Models from the original project brief (Gemini 1.5) are no longer available.
CURRENT_DEFAULT_MODEL = "gemini-3.8-flash"


def _normalized_api_key() -> str:
    """Return a cleaned API key without exposing it in logs."""
    key = (settings.gemini_api_key or "").strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in {'"', "'"}:
        key = key[1:-1].strip()
    return key


def _client():
    key = _normalized_api_key()
    if not key:
        return None

    try:
        from google import genai
    except ImportError as exc:
        raise GeminiIntegrationError(
            "google-genai is not installed in the active virtual environment. "
            "Run: python -m pip install -U google-genai"
        ) from exc

    try:
        return genai.Client(api_key=key)
    except Exception as exc:
        raise GeminiIntegrationError(f"Could not initialize Gemini client: {exc}") from exc


def _schema_hint() -> str:
    # Kept as a compact hint for older/alternate Gemini SDK configurations.
    return json.dumps(
        {
            "total_budget": 0,
            "allocated_budget": 0,
            "remaining_budget": 0,
            "overview": "",
            "budget_breakdown": [
                {
                    "category": "",
                    "allocation": 0,
                    "percentage_of_budget": 0,
                    "items": [
                        {
                            "name": "",
                            "description": "",
                            "estimated_price": 0,
                            "quantity": 1,
                            "platform": "Amazon",
                            "search_terms": "",
                            "shopping_links": {},
                        }
                    ],
                }
            ],
            "outfit_analysis": {
                "dominant_colors": [],
                "style": "",
                "formality": "",
                "notes": "",
            },
            "styling_tips": [],
            "additional_suggestions": [],
            "source": "gemini",
            "warnings": [],
        },
        indent=2,
    )


def _strip_code_fence(text: str) -> str:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            cleaned = cleaned[first_newline + 1:]
        else:
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    return cleaned.strip()


def _remove_json_comments(text: str) -> str:
    """Remove // and /* */ comments while preserving quoted strings."""
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "/":
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            continue

        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def _repair_common_json(text: str) -> str:
    """Repair small, common LLM JSON formatting mistakes using only stdlib."""
    text = _remove_json_comments(text)

    # Normalize typographic quotes sometimes emitted by a model.
    text = (
        text.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("“", '"')
        .replace("”", '"')
    )

    # Remove trailing commas before } or ]. Do this outside strings.
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == ",":
            j = i + 1
            while j < len(text) and text[j].isspace():
                j += 1
            if j < len(text) and text[j] in "}]":
                i = j
                out.append(text[j])
                i += 1
                continue

        out.append(ch)
        i += 1

    text = "".join(out)

    # Quote simple bare object keys: { foo: 1 } -> { "foo": 1 }.
    # This runs only against tokens immediately following { or ,.
    import re
    text = re.sub(
        r'([\{,]\s*)([A-Za-z_][A-Za-z0-9_ -]*?)(\s*:)',
        lambda m: f'{m.group(1)}"{m.group(2).strip()}"{m.group(3)}',
        text,
    )
    return text


def _safe_json(text: str) -> dict[str, Any]:
    """Parse Gemini JSON and tolerate common LLM formatting mistakes."""
    cleaned = _strip_code_fence(text)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Gemini returned no JSON object")

    candidate = cleaned[start:end + 1]

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as strict_exc:
        repaired = _repair_common_json(candidate)
        try:
            parsed = json.loads(repaired)
        except json.JSONDecodeError as repair_exc:
            raise ValueError(
                f"Gemini returned malformed JSON: {repair_exc}"
            ) from strict_exc

    if not isinstance(parsed, dict):
        raise ValueError("Gemini returned JSON, but the top-level value is not an object")
    return parsed


def _platform_key(platform: str) -> str:
    p = platform.strip().lower()
    aliases = {
        "amazon india": "amazon",
        "amazon": "amazon",
        "flipkart": "flipkart",
        "ikea": "ikea",
        "swiggy": "swiggy",
        "zomato": "zomato",
        "oyo": "oyo",
        "myntra": "myntra",
        "google": "google",
    }
    return aliases.get(p, "")


def _enforce_budget(parsed: RecommendationResponse, budget: float) -> tuple[float, bool]:
    """Ensure the final plan never exceeds the user's actual budget.

    We never fabricate cheaper prices. Instead we reduce quantities and, when a single
    unit is still unaffordable, remove that line item. The user therefore gets a plan
    whose arithmetic is guaranteed to fit the stated budget while preserving genuine
    Gemini-estimated unit prices.
    """
    changed = False
    remaining = round(budget, 2)

    for section in parsed.budget_breakdown:
        kept_items = []
        for item in section.items:
            unit_price = max(0.0, float(item.estimated_price))
            quantity = max(1, int(item.quantity))

            if unit_price <= 0:
                item.quantity = quantity
                kept_items.append(item)
                continue

            affordable_qty = min(quantity, int((remaining + 1e-9) / unit_price))
            if affordable_qty < quantity:
                changed = True

            if affordable_qty <= 0:
                changed = True
                continue

            item.quantity = affordable_qty
            kept_items.append(item)
            remaining = round(remaining - (unit_price * affordable_qty), 2)

        section.items = kept_items

    allocated = round(budget - remaining, 2)
    return allocated, changed


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        if isinstance(value, str):
            cleaned = value.replace(",", "").replace("₹", "").replace("INR", "").strip()
            return float(cleaned)
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 1) -> int:
    try:
        return max(1, int(float(value)))
    except (TypeError, ValueError):
        return default


def _item_from_gemini(raw: Any, category: str) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None

    name = str(raw.get("name") or raw.get("product_name") or raw.get("item") or raw.get("title") or "").strip()
    if not name:
        return None

    description = str(raw.get("description") or raw.get("details") or raw.get("reason") or "").strip()
    price = _coerce_float(
        raw.get("estimated_price", raw.get("price", raw.get("unit_price", raw.get("cost", 0))))
    )
    quantity = _coerce_int(raw.get("quantity", raw.get("qty", 1)))
    platform = str(raw.get("platform") or raw.get("source") or "Amazon").strip()
    search_terms = str(raw.get("search_terms") or raw.get("search_term") or name).strip()
    links = raw.get("shopping_links") if isinstance(raw.get("shopping_links"), dict) else {}

    return {
        "name": name,
        "description": description or f"{name} recommendation for {category.lower()}.",
        "estimated_price": max(0.0, price),
        "quantity": quantity,
        "platform": platform,
        "search_terms": search_terms,
        "shopping_links": links,
    }


def _extract_gemini_breakdown(data: dict[str, Any], fallback: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize several reasonable Gemini JSON shapes into PocketSmart's schema.

    Gemini may return a compact response with only total_budget/remaining_budget,
    a `recommendations` list, or a partially populated `budget_breakdown`. Rather than
    failing the entire request, normalize what is usable and fall back to the local
    starter structure only for missing sections.
    """
    raw_breakdown = data.get("budget_breakdown")
    if isinstance(raw_breakdown, list) and raw_breakdown:
        normalized: list[dict[str, Any]] = []
        for raw_section in raw_breakdown:
            if not isinstance(raw_section, dict):
                continue
            category = str(raw_section.get("category") or raw_section.get("name") or "Recommendations").strip()
            raw_items = raw_section.get("items")
            if not isinstance(raw_items, list):
                raw_items = raw_section.get("recommendations") if isinstance(raw_section.get("recommendations"), list) else []
            items: list[dict[str, Any]] = []
            for raw_item in raw_items:
                item = _item_from_gemini(raw_item, category)
                if item:
                    items.append(item)
            normalized.append(
                {
                    "category": category,
                    "allocation": _coerce_float(raw_section.get("allocation", 0)),
                    "percentage_of_budget": _coerce_float(raw_section.get("percentage_of_budget", raw_section.get("percentage", 0))),
                    "items": items,
                }
            )
        if normalized:
            return normalized

    # Common compact Gemini shape: {"recommendations": [{...}, ...]}
    raw_recs = data.get("recommendations")
    if isinstance(raw_recs, list) and raw_recs:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for raw_item in raw_recs:
            if not isinstance(raw_item, dict):
                continue
            category = str(raw_item.get("category") or raw_item.get("type") or "Recommendations").strip()
            item = _item_from_gemini(raw_item, category)
            if item:
                grouped.setdefault(category, []).append(item)
        if grouped:
            return [
                {"category": category, "allocation": 0, "percentage_of_budget": 0, "items": items}
                for category, items in grouped.items()
            ]

    # Some responses put categories/items in an object.
    raw_categories = data.get("categories")
    if isinstance(raw_categories, list) and raw_categories:
        converted: list[dict[str, Any]] = []
        for raw_category in raw_categories:
            if not isinstance(raw_category, dict):
                continue
            category = str(raw_category.get("category") or raw_category.get("name") or "Recommendations").strip()
            raw_items = raw_category.get("items") or raw_category.get("recommendations")
            if not isinstance(raw_items, list):
                continue
            items = [
                item
                for raw_item in raw_items
                if (item := _item_from_gemini(raw_item, category)) is not None
            ]
            if items:
                converted.append({"category": category, "allocation": 0, "percentage_of_budget": 0, "items": items})
        if converted:
            return converted

    # Last resort: retain a known-good local structure so a compact Gemini response
    # still renders as a valid PocketSmart plan.
    fallback_breakdown = fallback.get("budget_breakdown")
    return fallback_breakdown if isinstance(fallback_breakdown, list) else []


def _normalize_outfit_analysis(value: Any, fallback: Any = None) -> OutfitAnalysis | None:
    """Normalize Gemini's outfit_analysis field.

    Some Gemini responses return the analysis as a plain string instead of the
    structured object expected by PocketSmart. Preserve that useful text as notes.
    """
    if value is None:
        if isinstance(fallback, OutfitAnalysis):
            return fallback
        if isinstance(fallback, dict):
            try:
                return OutfitAnalysis.model_validate(fallback)
            except ValidationError:
                return None
        return None

    if isinstance(value, OutfitAnalysis):
        return value

    if isinstance(value, dict):
        colors = value.get("dominant_colors", value.get("colors", []))
        if isinstance(colors, str):
            colors = [c.strip() for c in colors.split(",") if c.strip()]
        if not isinstance(colors, list):
            colors = []
        return OutfitAnalysis(
            dominant_colors=[str(c).strip() for c in colors if str(c).strip()],
            style=str(value.get("style") or value.get("outfit_style") or ""),
            formality=str(value.get("formality") or value.get("occasion_formality") or ""),
            notes=str(value.get("notes") or value.get("analysis") or value.get("description") or ""),
        )

    if isinstance(value, str) and value.strip():
        return OutfitAnalysis(
            dominant_colors=[],
            style="",
            formality="",
            notes=value.strip(),
        )

    return None


def _normalize_before_validation(
    data: dict[str, Any],
    fallback: dict[str, Any],
    requested_budget: float | None,
) -> tuple[dict[str, Any], bool]:
    """Fill omitted fields before Pydantic validation.

    Returns (normalized_data, used_fallback_structure). The user's requested budget is
    authoritative. Gemini is allowed to omit computed totals because PocketSmart can
    calculate them from the item-level estimates.
    """
    if not isinstance(data, dict):
        raise GeminiIntegrationError("Gemini returned a JSON value that is not an object.")

    result = dict(data)
    user_budget = _coerce_float(requested_budget, 0.0) if requested_budget is not None else _coerce_float(result.get("total_budget"), 0.0)
    if user_budget <= 0:
        raise GeminiIntegrationError("PocketSmart received an invalid total budget from Gemini/user input.")

    result["total_budget"] = user_budget

    used_fallback_structure = False
    if not result.get("overview"):
        result["overview"] = fallback.get("overview", "Gemini generated a budget recommendation.")

    if not isinstance(result.get("budget_breakdown"), list) or not result.get("budget_breakdown"):
        normalized_breakdown = _extract_gemini_breakdown(result, fallback)
        if normalized_breakdown is fallback.get("budget_breakdown"):
            used_fallback_structure = True
        result["budget_breakdown"] = normalized_breakdown

    # These are computed later in _post_process, so placeholders are sufficient.
    result["allocated_budget"] = _coerce_float(result.get("allocated_budget"), 0.0)
    remaining_value = result.get("remaining_budget")
    result["remaining_budget"] = _coerce_float(remaining_value, user_budget)

    result["outfit_analysis"] = _normalize_outfit_analysis(
        result.get("outfit_analysis"),
        fallback.get("outfit_analysis"),
    )
    result.setdefault("styling_tips", fallback.get("styling_tips", []))
    result.setdefault("additional_suggestions", fallback.get("additional_suggestions", []))
    result.setdefault("source", "gemini")
    result.setdefault("warnings", [])

    return result, used_fallback_structure


def _post_process(
    data: dict[str, Any],
    fallback: dict[str, Any],
    requested_budget: float | None = None,
) -> dict[str, Any]:
    # Preserve Gemini's originally reported totals before normalization so warnings
    # can accurately describe what was changed.
    original_model_budget = _coerce_float(data.get("total_budget"), 0.0) if isinstance(data, dict) else 0.0
    original_model_allocated = _coerce_float(data.get("allocated_budget"), 0.0) if isinstance(data, dict) else 0.0
    normalized, used_fallback_structure = _normalize_before_validation(data, fallback, requested_budget)

    try:
        parsed = RecommendationResponse.model_validate(normalized)
    except ValidationError as exc:
        # Give the caller one useful error only after normalization genuinely failed.
        raise GeminiIntegrationError(
            "Gemini returned JSON, but PocketSmart could not normalize it into the recommendation schema. "
            f"Validation error: {exc}"
        ) from exc

    # The user's submitted budget is authoritative. Never trust a model-generated
    # total_budget field when calculating budget adherence.
    model_budget = original_model_budget if original_model_budget > 0 else float(parsed.total_budget)
    total_budget = float(requested_budget if requested_budget is not None else model_budget)
    if total_budget <= 0:
        raise GeminiIntegrationError("PocketSmart received an invalid total budget.")

    allocated_before_fit = 0.0
    for section in parsed.budget_breakdown:
        section_total = 0.0
        for item in section.items:
            item.quantity = max(1, int(item.quantity))
            section_total += max(0.0, float(item.estimated_price)) * item.quantity
            platform_key = _platform_key(item.platform)
            platforms = (
                platform_keys_for_category(section.category)
                if platform_key == ""
                else [platform_key]
            )
            item.shopping_links = build_search_links(
                platforms,
                item.search_terms or item.name,
            )
        section.allocation = round(section_total, 2)
        section.percentage_of_budget = (
            round((section_total / total_budget) * 100, 2) if total_budget else 0
        )
        allocated_before_fit += section_total

    allocated, changed = _enforce_budget(parsed, total_budget)

    # Recalculate section totals after enforcing the budget.
    for section in parsed.budget_breakdown:
        section_total = round(
            sum(
                max(0.0, float(item.estimated_price)) * max(1, int(item.quantity))
                for item in section.items
            ),
            2,
        )
        section.allocation = section_total
        section.percentage_of_budget = (
            round((section_total / total_budget) * 100, 2) if total_budget else 0
        )

    if abs(model_budget - total_budget) > 0.01:
        parsed.warnings.append(
            f"Gemini returned total_budget INR {model_budget:.2f}; PocketSmart normalized it to the user's budget of INR {total_budget:.2f}."
        )

    if changed or allocated_before_fit > total_budget + 0.01 or original_model_allocated > total_budget + 0.01:
        parsed.warnings.append(
            "Gemini's first draft exceeded the user's budget, so PocketSmart reduced quantities or removed unaffordable items without changing estimated unit prices."
        )

    if used_fallback_structure:
        parsed.warnings.append(
            "Gemini returned an incomplete recommendation structure, so PocketSmart used its local starter structure for the missing recommendation fields."
        )

    parsed.total_budget = round(total_budget, 2)
    parsed.allocated_budget = round(allocated, 2)
    parsed.remaining_budget = round(total_budget - allocated, 2)
    parsed.source = "gemini"
    parsed.warnings = list(
        dict.fromkeys(
            parsed.warnings
            + [
                "Prices and availability are estimates unless backed by a verified marketplace feed.",
            ]
        )
    )
    return parsed.model_dump()

def _generate(
    prompt: str,
    fallback: dict[str, Any],
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
    requested_budget: float | None = None,
) -> dict[str, Any]:
    client = _client()
    if client is None:
        # No key means local fallback is intentional.
        return fallback

    try:
        from google.genai import types

        contents: list[Any] = [prompt]
        if image_bytes and mime_type:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

        config_kwargs: dict[str, Any] = {
            "system_instruction": SYSTEM_INSTRUCTION,
            "response_mime_type": "application/json",
            "temperature": settings.gemini_temperature,
            "max_output_tokens": settings.gemini_max_output_tokens,
        }

        # Gemini 3.x supports thinking levels. Keep this low for this structured,
        # latency-sensitive recommendation workflow.
        if hasattr(types, "ThinkingConfig"):
            config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level="low")

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(**config_kwargs),
        )

        # The current SDK can return an already-parsed Pydantic object when a response
        # schema is supplied. Fall back to JSON text for compatibility.
        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            if isinstance(parsed, RecommendationResponse):
                data = parsed.model_dump()
            elif isinstance(parsed, dict):
                data = parsed
            else:
                data = _safe_json(str(parsed))
        else:
            data = _safe_json(response.text or "")

        return _post_process(data, fallback, requested_budget=requested_budget)
    except GeminiIntegrationError:
        raise
    except Exception as exc:
        logger.exception(
            "Gemini request failed. model=%s image=%s",
            settings.gemini_model,
            bool(image_bytes),
        )
        if settings.gemini_fallback_on_error:
            fallback["warnings"] = list(dict.fromkeys(
                fallback.get("warnings", [])
                + [f"Gemini error: {type(exc).__name__}. Local fallback used because GEMINI_FALLBACK_ON_ERROR=true."]
            ))
            return fallback
        raise GeminiIntegrationError(
            f"Gemini request failed for model '{settings.gemini_model}': {exc}"
        ) from exc


def generate_home_recommendations(data: dict[str, Any]) -> dict[str, Any]:
    budget = float(data["total_budget"])
    prompt = f"""
Create a home interior budget plan for India.
Total budget: INR {budget:.2f}
Lights/fixtures: {data.get('num_lights', 0)}
Ceiling fans: {data.get('num_fans', 0)}
Furniture pieces: {data.get('num_furniture', 0)}
Dining tables: {data.get('num_dining_tables', 0)}
Rooms: {', '.join(data.get('rooms', [])) or 'Not specified'}
Additional requirements: {data.get('additional_requirements') or 'None'}
Prefer practical options across IKEA, Amazon, and Flipkart. Allocate the budget by category,
recommend only items whose quantity * estimated_price fits within the total budget. The total_budget field must equal the submitted budget exactly. The sum of all line items must be <= the submitted budget. If the requested quantities cannot all fit, prioritize essential low-cost options and reduce quantities. Provide search terms instead of URLs.
Return JSON matching the response schema. Example shape:
{_schema_hint()}
""".strip()
    return _generate(prompt, home_fallback(budget), requested_budget=budget)


def generate_party_recommendations(data: dict[str, Any]) -> dict[str, Any]:
    budget = float(data["total_budget"])
    prompt = f"""
Create a party budget plan for India.
Total budget: INR {budget:.2f}
Guests: {data.get('num_guests', 0)}
Party type: {data.get('party_type', '')}
Venue type: {data.get('venue_type', '')}
Catering needed: {data.get('needs_catering', False)}
Decoration needed: {data.get('needs_decoration', False)}
Entertainment needed: {data.get('needs_entertainment', False)}
Additional requirements: {data.get('additional_requirements') or 'None'}
Consider Swiggy/Zomato for catering, OYO or venue search for accommodation/venue discovery,
and Amazon/Flipkart for decor where useful. Keep the complete plan within the total budget. The total_budget field must equal the submitted budget exactly and the sum of all line items must be <= that budget. If the requested services cannot all fit, reduce quantities or omit optional items. Provide search terms instead of URLs. Return JSON matching the response schema.
""".strip()
    return _generate(prompt, party_fallback(budget), requested_budget=budget)


def generate_jewelry_recommendations(
    data: dict[str, Any],
    image_bytes: bytes | None,
    mime_type: str | None,
) -> dict[str, Any]:
    budget = float(data["total_budget"])
    prompt = f"""
Create a jewelry recommendation plan for India.
Total budget: INR {budget:.2f}
Occasion: {data.get('occasion', '')}
Style preferences: {data.get('preferences') or 'None'}
The user may have supplied an outfit image. Analyze it only for visible colors, style cues,
and formality; do not identify the person and do not infer sensitive traits. Recommend jewelry that fits the budget. The total_budget field must equal the submitted budget exactly and the sum of all line items must be <= that budget. Do not increase the budget to accommodate a preferred item. Favor Amazon and Flipkart search terms; Myntra may be used for fashion
accessories. Return no direct URLs. Return JSON matching the response schema.
""".strip()
    return _generate(
        prompt,
        jewelry_fallback(budget),
        image_bytes=image_bytes,
        mime_type=mime_type,
        requested_budget=budget,
    )
```

## `app/services/history_service.py`

```python
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Recommendation


def save_recommendation(
    db: Session,
    user_id: int,
    recommendation_type: str,
    input_data: dict,
    result: dict,
    image_filename: str | None = None,
) -> Recommendation:
    summary = result.get("overview", "Recommendation generated")
    row = Recommendation(
        user_id=user_id,
        recommendation_type=recommendation_type,
        input_data=input_data,
        result=result,
        result_summary=summary,
        image_filename=image_filename,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_recommendations(db: Session, user_id: int, limit: int = 50) -> list[Recommendation]:
    statement = select(Recommendation).where(Recommendation.user_id == user_id).order_by(Recommendation.created_at.desc()).limit(limit)
    return list(db.scalars(statement))


def get_recommendation(db: Session, user_id: int, recommendation_id: int) -> Recommendation | None:
    return db.scalar(select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.user_id == user_id))
```

## `app/services/image_service.py`

```python
from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image(content: bytes, mime_type: str, max_bytes: int) -> None:
    if mime_type not in ALLOWED_TYPES:
        raise ValueError("Only JPG, PNG and WEBP images are supported.")
    if len(content) > max_bytes:
        raise ValueError("The uploaded image is too large.")
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValueError("The uploaded file is not a valid image.")
```

## `app/services/recommendation_engine.py`

```python
from __future__ import annotations

from typing import Any

from .fallback import home_fallback, jewelry_fallback, party_fallback
from .gemini_utils import generate_home_recommendations, generate_jewelry_recommendations, generate_party_recommendations


def recommend_home(data: dict[str, Any]) -> dict:
    return generate_home_recommendations(data) if data else home_fallback(0)


def recommend_party(data: dict[str, Any]) -> dict:
    return generate_party_recommendations(data) if data else party_fallback(0)


def recommend_jewelry(data: dict[str, Any], image_bytes: bytes | None, mime_type: str | None) -> dict:
    return generate_jewelry_recommendations(data, image_bytes, mime_type) if data else jewelry_fallback(0)
```

## `app/static/css/styles.css`

```css
:root{--navy:#12335b;--blue:#2b6cb0;--soft:#f4f7fb;--ink:#1f2a37;--muted:#6b7280;--line:#d9e1ec;--white:#fff;--shadow:0 18px 45px rgba(18,51,91,.10);--radius:18px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:#fff;line-height:1.55}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}.topbar{background:var(--navy);color:#fff;position:sticky;top:0;z-index:20}.nav-wrap{max-width:1180px;margin:auto;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;gap:24px}.brand{font-weight:800;font-size:20px;color:#fff}.nav-links{display:flex;gap:18px;align-items:center;flex-wrap:wrap}.nav-links a{color:#fff;font-size:14px;opacity:.92}.nav-cta{padding:10px 14px;border-radius:999px;background:#fff;color:var(--navy)!important;opacity:1!important}.hero{background:linear-gradient(135deg,#153b68,#2f6fae);color:#fff}.hero-inner{max-width:1180px;margin:auto;padding:110px 24px 100px}.eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:12px;font-weight:800;opacity:.8}.hero h1,.page-hero h1,.dashboard-hero h1{font-size:clamp(38px,6vw,64px);line-height:1.05;margin:14px 0}.hero p{max-width:700px;font-size:18px;opacity:.92}.hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}.btn{display:inline-flex;align-items:center;justify-content:center;border:none;border-radius:12px;padding:12px 18px;font-weight:700;cursor:pointer;font-size:14px}.btn.primary{background:var(--blue);color:#fff}.btn.secondary{background:#fff;color:var(--navy);border:1px solid var(--line)}.btn.light{background:#fff;color:var(--navy)}.btn.outline-light{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.55)}.btn.wide{width:100%}.btn:disabled{opacity:.6;cursor:wait}.hero .btn.primary{background:#fff;color:var(--navy)}.hero .btn.secondary{background:transparent;color:#fff;border-color:rgba(255,255,255,.5)}.hero-note{margin-top:20px;font-size:13px;opacity:.78}.section{max-width:1180px;margin:auto;padding:82px 24px}.section.compact{padding-top:48px}.soft{max-width:none;background:var(--soft)}.section-head{max-width:800px;margin:0 auto 30px;text-align:center}.section-head h2,.section-title-row h2{font-size:34px;line-height:1.15;margin:8px 0 12px}.grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.grid-2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.feature-card,.planner-card,.history-card,.quote-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}.feature-card{padding:28px}.feature-card .icon{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:#e8f1fb;color:var(--blue);font-size:26px}.feature-card h3{margin:18px 0 10px}.feature-card p{color:var(--muted)}.steps{max-width:1080px;margin:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.steps>div{background:#fff;padding:26px;border-radius:16px;border:1px solid var(--line)}.steps strong{font-size:28px;color:var(--blue)}.cta-band{background:var(--navy);color:#fff;padding:58px max(24px,calc((100vw - 1180px)/2));display:flex;justify-content:space-between;align-items:center;gap:24px}.cta-band h2{margin:8px 0 0;font-size:34px}.footer{background:#0e2948;color:#dbe7f5;padding:24px;display:flex;justify-content:center;gap:20px;flex-wrap:wrap;font-size:13px}.footer a{color:#dbe7f5}.flash{max-width:1180px;margin:16px auto;padding:12px 18px;border-radius:12px}.flash.error,.notice.error{background:#fff0f0;color:#9b1c1c;border:1px solid #f2cccc}.page-hero,.dashboard-hero{background:linear-gradient(135deg,#edf4fb,#fff);padding:70px 24px;text-align:center}.page-hero p,.dashboard-hero p{max-width:740px;margin:0 auto;color:var(--muted)}.planner-card{overflow:hidden}.planner-image{height:170px;background-size:cover}.home-art{background:linear-gradient(135deg,#c8d5e2,#edf4fb)}.party-art{background:linear-gradient(135deg,#f3d6df,#fef2f7)}.jewelry-art{background:linear-gradient(135deg,#e7ddd4,#fbf7f3)}.planner-body{padding:22px}.planner-body p{color:var(--muted);min-height:74px}.section-title-row{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}.history-list{border:1px solid var(--line);border-radius:16px;overflow:hidden}.history-row{display:grid;grid-template-columns:140px 1fr 160px 80px;gap:16px;padding:16px 18px;border-bottom:1px solid var(--line);align-items:center}.history-row:last-child{border-bottom:none}.history-type{font-weight:800}.history-summary{color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.history-date{font-size:13px;color:var(--muted)}.empty-state{padding:44px;text-align:center;border:1px dashed var(--line);border-radius:16px;color:var(--muted)}.auth-shell{min-height:calc(100vh - 140px);display:grid;place-items:center;padding:70px 24px;background:var(--soft)}.auth-card{width:min(540px,100%);background:#fff;border:1px solid var(--line);border-radius:24px;padding:36px;box-shadow:var(--shadow)}.auth-brand{text-align:center;font-size:36px;font-weight:900;color:var(--blue)}.auth-subtitle{text-align:center;color:var(--muted);margin-bottom:26px}.auth-card h1{font-size:32px;margin:0 0 24px}.form-stack{display:grid;gap:16px}.form-stack label,.planner-form label{display:grid;gap:7px;font-weight:700;font-size:14px}.form-stack input,.planner-form input,.planner-form select,.planner-form textarea{width:100%;padding:12px 13px;border-radius:12px;border:1px solid var(--line);font:inherit;background:#fff}.planner-form{background:#fff;border:1px solid var(--line);border-radius:20px;box-shadow:var(--shadow);padding:24px;max-width:900px;margin:auto}.form-section{padding:18px;background:#f8fafc;border-radius:16px;margin-bottom:16px}.form-section h2{font-size:18px;margin:0 0 16px}.check-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.check{display:flex!important;grid-template-columns:none!important;align-items:center;gap:8px!important;padding:12px;border:1px solid var(--line);border-radius:12px;background:#fff}.upload-box{border:2px dashed var(--line);padding:28px;display:grid!important;place-items:center;gap:12px;cursor:pointer;text-align:center}.upload-box input{width:auto}.image-preview{max-width:240px;max-height:320px;border-radius:14px;border:1px solid var(--line)}.loading{margin-top:12px;text-align:center;color:var(--muted)}.result-slot{max-width:1000px;margin:36px auto 0}.recommendation-head{background:linear-gradient(135deg,#153b68,#2f6fae);color:#fff;padding:28px;border-radius:18px;display:flex;justify-content:space-between;gap:22px;align-items:flex-start}.recommendation-head h2{margin:0 0 8px}.recommendation-head p{opacity:.9}.budget-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;min-width:390px}.budget-metrics div,.analysis-grid div{background:rgba(255,255,255,.12);padding:14px;border-radius:12px}.budget-metrics span,.analysis-grid span,.history-metrics span{display:block;font-size:12px;opacity:.75}.budget-metrics strong{font-size:18px}.result-section{margin-top:24px}.result-section h2{font-size:24px}.category-section{margin-top:16px}.category-title{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:14px;background:#eef5fc;border-radius:14px}.pill{display:inline-flex;padding:6px 10px;border-radius:999px;background:#dbeafb;color:var(--blue);font-size:12px;font-weight:800}.recommendation-card{margin-top:10px;padding:18px;border:1px solid var(--line);border-radius:16px;display:flex;justify-content:space-between;gap:18px;background:#fff}.rec-main h3{margin:0 0 6px}.rec-main p{margin:0;color:var(--muted)}.rec-meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--muted)}.shop-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.shop-links a{font-size:12px;padding:7px 9px;border:1px solid var(--line);border-radius:10px}.rec-price{font-weight:900;font-size:18px;white-space:nowrap;text-align:right}.rec-price small{display:block;font-size:10px;color:var(--muted);font-weight:600}.analysis-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;color:var(--ink)}.analysis-grid div{background:#f4f7fb}.analysis-grid span{color:var(--muted);opacity:1}.analysis-grid strong{display:block;margin-top:5px}.plain-list{padding-left:20px}.notice{margin-top:20px;padding:14px 16px;border-radius:12px;background:#fff8e8;border:1px solid #f4ddaa;color:#785d14}.detail-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:30px}.history-card{padding:22px}.history-card-top{display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:12px}.history-card h3{font-size:18px;min-height:56px}.history-metrics{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:18px 0}.history-metrics div{padding:12px;border:1px solid var(--line);border-radius:12px}.quote-card{padding:24px}.quote-card p{font-size:18px}.quote-card strong{font-size:13px;color:var(--muted)}.auth-foot{text-align:center;color:var(--muted);margin-top:18px}
@media(max-width:900px){.grid-3,.steps{grid-template-columns:1fr}.nav-wrap{align-items:flex-start}.nav-links{justify-content:flex-end}.cta-band{flex-direction:column;align-items:flex-start}.budget-metrics{min-width:0;width:100%}.recommendation-head{flex-direction:column}.history-row{grid-template-columns:1fr}.grid-2{grid-template-columns:1fr}}
@media(max-width:650px){.nav-links{gap:10px}.nav-links a{font-size:12px}.hero-inner{padding:80px 20px}.section{padding:60px 20px}.check-grid,.analysis-grid,.budget-metrics{grid-template-columns:1fr}.planner-form{padding:16px}.recommendation-card{flex-direction:column}.rec-price{text-align:left}.auth-card{padding:24px}}
```

## `app/static/favicon.svg`

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#12335b"/><path d="M14 44 27 20h10l13 24H39l-3-6H28l-3 6z" fill="#fff"/></svg>
```

## `app/static/js/app.js`

```javascript
document.addEventListener('click', (event) => {
  const link = event.target.closest('a[href^="#"]');
  if (!link) return;
  const target = document.querySelector(link.getAttribute('href'));
  if (target) {
    event.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});
```

## `app/static/js/planner.js`

```javascript
(function () {
  function money(value) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(value || 0));
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'\"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' }[char]));
  }

  function renderResult(payload) {
    const result = payload.result;
    const results = document.querySelector('[data-results]');
    if (!results) return;
    const sections = (result.budget_breakdown || []).map((section) => `
      <div class="category-section">
        <div class="category-title"><span class="pill">${escapeHtml(section.category)}</span><div><strong>${money(section.allocation)}</strong> <span>${Number(section.percentage_of_budget || 0).toFixed(2)}%</span></div></div>
        ${(section.items || []).map((item) => `<article class="recommendation-card"><div class="rec-main"><h3>${escapeHtml(item.name)}</h3><p>${escapeHtml(item.description)}</p><div class="rec-meta"><span>${escapeHtml(item.platform)}</span><span>Qty: ${escapeHtml(item.quantity)}</span><span>${escapeHtml(item.search_terms)}</span></div><div class="shop-links">${Object.entries(item.shopping_links || {}).map(([platform, url]) => `<a target="_blank" rel="noopener noreferrer" href="${escapeHtml(url)}">Shop on ${escapeHtml(platform)} ↗</a>`).join('')}</div></div><div class="rec-price">${money(item.estimated_price)}<small>estimated</small></div></article>`).join('')}
      </div>`).join('');
    results.innerHTML = `<div class="recommendation-head"><div><h2>Plan generated</h2><p>${escapeHtml(result.overview)}</p><a href="${escapeHtml(payload.details_url)}">Open full details →</a></div><div class="budget-metrics"><div><span>Total Budget</span><strong>${money(result.total_budget)}</strong></div><div><span>Allocated</span><strong>${money(result.allocated_budget)}</strong></div><div><span>Remaining</span><strong>${money(result.remaining_budget)}</strong></div></div></div><section class="result-section"><h2>Recommendations</h2><div class="recommendation-list">${sections}</div></section>${(result.warnings || []).map((warning) => `<div class="notice">${escapeHtml(warning)}</div>`).join('')}`;
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  document.querySelectorAll('[data-planner-form]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const loading = form.querySelector('[data-loading]');
      const button = form.querySelector('button[type="submit"]');
      if (loading) loading.hidden = false;
      if (button) button.disabled = true;
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(form),
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.detail || 'Request failed');
        renderResult(payload);
      } catch (error) {
        const results = document.querySelector('[data-results]');
        if (results) results.innerHTML = `<div class="notice error">${escapeHtml(error.message || 'Unable to generate recommendations.')}</div>`;
      } finally {
        if (loading) loading.hidden = true;
        if (button) button.disabled = false;
      }
    });
  });

  const file = document.querySelector('#outfit-image');
  const preview = document.querySelector('#image-preview');
  if (file && preview) {
    file.addEventListener('change', () => {
      const chosen = file.files?.[0];
      if (!chosen) { preview.hidden = true; preview.removeAttribute('src'); return; }
      preview.src = URL.createObjectURL(chosen);
      preview.hidden = false;
    });
  }
})();
```

## `app/templates/404.html`

```html
{% extends "base.html" %}
{% block title %}Not Found — PocketSmart AI{% endblock %}
{% block content %}<section class="page-hero"><span class="eyebrow">404</span><h1>Page not found.</h1><p>The page you requested does not exist.</p><a class="btn primary" href="/">Return Home</a></section>{% endblock %}
```

## `app/templates/base.html`

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}PocketSmart AI{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', path='css/styles.css') }}">
</head>
<body>
<header class="topbar">
  <div class="nav-wrap">
    <a class="brand" href="{{ '/dashboard' if user else '/' }}">PocketSmart</a>
    {% if user %}
    <nav class="nav-links">
      <a href="/dashboard">Dashboard</a>
      <a href="/home-planner">Home Planner</a>
      <a href="/party-planner">Party Planner</a>
      <a href="/jewelry-planner">Jewelry Planner</a>
      <a href="/history">History</a>
      <a href="/logout">Logout</a>
    </nav>
    {% else %}
    <nav class="nav-links">
      <a href="/#features">Features</a>
      <a href="/testimonials">Testimonials</a>
      <a href="/login">Sign in</a>
      <a class="nav-cta" href="/register">Get Started</a>
    </nav>
    {% endif %}
  </div>
</header>

{% if error %}
<div class="flash error">{{ error }}</div>
{% endif %}
{% if errors %}
<div class="flash error">{% for e in errors %}<div>{{ e }}</div>{% endfor %}</div>
{% endif %}

<main>
{% block content %}{% endblock %}
</main>

<footer class="footer">
  <div>© 2026 PocketSmart AI. Budget planning assistant.</div>
  <div class="footer-links"><a href="/testimonials">Testimonials</a> · <a href="/docs">API Docs</a></div>
</footer>
<script src="{{ url_for('static', path='js/app.js') }}"></script>
{% block scripts %}{% endblock %}
</body>
</html>
```

## `app/templates/dashboard.html`

```html
{% extends "base.html" %}
{% block title %}Dashboard — PocketSmart AI{% endblock %}
{% block content %}
<section class="dashboard-hero"><div><span class="eyebrow">Personalized workspace</span><h1>Welcome, {{ user.username }}!</h1><p>Choose a budget planner to get started with your personalized planning experience.</p></div></section>
<section class="section compact">
  <div class="grid-3">
    <article class="planner-card"><div class="planner-image home-art"></div><div class="planner-body"><h3>⌂ Home Budget Planner</h3><p>Plan an interior budget with recommendations for furniture, lighting and more.</p><a class="btn primary" href="/home-planner">Get Started</a></div></article>
    <article class="planner-card"><div class="planner-image party-art"></div><div class="planner-body"><h3>✦ Party Budget Planner</h3><p>Plan an event with budget allocations for food, decoration, venue and entertainment.</p><a class="btn primary" href="/party-planner">Get Started</a></div></article>
    <article class="planner-card"><div class="planner-image jewelry-art"></div><div class="planner-body"><h3>◇ Jewelry Budget Planner</h3><p>Find jewelry ideas that match an occasion and your chosen budget.</p><a class="btn primary" href="/jewelry-planner">Get Started</a></div></article>
  </div>
</section>
<section class="section compact">
  <div class="section-title-row"><h2>Recent Activity</h2><a href="/history">View all history →</a></div>
  {% if history %}<div class="history-list">{% for item in history %}<div class="history-row"><div class="history-type">{{ item.recommendation_type|title }}</div><div class="history-summary">{{ item.result_summary }}</div><div class="history-date">{{ item.created_at.strftime('%d %b %Y %H:%M') }}</div><a href="/recommendations-details/{{ item.id }}">View</a></div>{% endfor %}</div>{% else %}<div class="empty-state">No recommendations yet. Start with one of the planners above.</div>{% endif %}
</section>
{% endblock %}
```

## `app/templates/history.html`

```html
{% extends "base.html" %}
{% block title %}Recommendation History — PocketSmart AI{% endblock %}
{% block content %}
<section class="page-hero"><span class="eyebrow">Your saved plans</span><h1>Your Recommendation History</h1><p>Review previous budget plans and open any saved recommendation in full.</p></section>
<section class="section compact">
  {% if history %}<div class="grid-3">{% for item in history %}
    <article class="history-card"><div class="history-card-top"><span class="pill">{{ item.recommendation_type|title }} Budget</span><span>{{ item.created_at.strftime('%d %b %Y') }}</span></div><h3>{{ item.result_summary[:90] }}{% if item.result_summary|length > 90 %}…{% endif %}</h3><div class="history-metrics"><div><span>Total</span><strong>₹{{ '%.2f'|format(item.result.get('total_budget', 0)) }}</strong></div><div><span>Remaining</span><strong>₹{{ '%.2f'|format(item.result.get('remaining_budget', 0)) }}</strong></div></div><a class="btn secondary wide" href="/recommendations-details/{{ item.id }}">View Full Details</a></article>
  {% endfor %}</div>{% else %}<div class="empty-state">No saved recommendations yet.</div>{% endif %}
</section>
{% endblock %}
```

## `app/templates/home_planner.html`

```html
{% extends "base.html" %}
{% block title %}Home Interior Planner — PocketSmart AI{% endblock %}
{% block content %}
<section class="page-hero"><span class="eyebrow">Home Interior Budget Planner</span><h1>Design within your budget.</h1><p>Set a total budget, tell us what you need, and PocketSmart will build a category-wise plan.</p></section>
<section class="section compact"><form class="planner-form" data-planner-form action="/generate-home" method="post">
  <div class="form-section"><h2>① Budget Details</h2><label>Total Budget (₹)<input type="number" name="total_budget" min="1" step="1" required value="50000"></label></div>
  <div class="form-section"><h2>② Fixtures & Furniture</h2><div class="grid-2"><label>Number of Lights / Fixtures<input type="number" name="num_lights" min="0" value="4"></label><label>Number of Ceiling Fans<input type="number" name="num_fans" min="0" value="2"></label><label>Number of Furniture Pieces<input type="number" name="num_furniture" min="0" value="2"></label><label>Number of Dining Tables<input type="number" name="num_dining_tables" min="0" value="1"></label></div></div>
  <div class="form-section"><h2>③ Rooms to Include</h2><div class="check-grid">{% for room in ['Living Room','Kitchen','Bedroom','Dining Room','Balcony','Home Office'] %}<label class="check"><input type="checkbox" name="rooms" value="{{ room }}" {% if room in ['Living Room','Bedroom'] %}checked{% endif %}><span>{{ room }}</span></label>{% endfor %}</div></div>
  <div class="form-section"><h2>④ Additional Information</h2><label>Special Requirements or Preferences<textarea name="additional_requirements" rows="4" placeholder="e.g. warm lighting, minimalist look, rental-friendly furniture"></textarea></label></div>
  <button class="btn primary wide" type="submit">Generate Recommendations</button>
  <div class="loading" data-loading hidden>Generating your plan…</div>
</form><div data-results class="result-slot"></div></section>
{% endblock %}
{% block scripts %}<script src="{{ url_for('static', path='js/planner.js') }}"></script>{% endblock %}
```

## `app/templates/home_recommendations.html`

```html
{% extends "recommendations_details.html" %}
```

## `app/templates/index.html`

```html
{% extends "base.html" %}
{% block title %}PocketSmart AI — Smart Budget Planning{% endblock %}
{% block content %}
<section class="hero">
  <div class="hero-inner">
    <span class="eyebrow">AI-powered budget planning</span>
    <h1>Spend smarter on the things that matter.</h1>
    <p>Plan a home interior, organize a party, or match jewelry to an occasion — all around the budget you set.</p>
    <div class="hero-actions">
      <a class="btn primary" href="/register">Get Started</a>
      <a class="btn secondary" href="#features">Learn More</a>
    </div>
    <div class="hero-note">Gemini-enabled when configured · Deterministic fallback mode included</div>
  </div>
</section>

<section id="features" class="section">
  <div class="section-head">
    <span class="eyebrow">Our smart planners</span>
    <h2>Three planning modes, one budget-first workflow.</h2>
    <p>Each planner gathers a different set of inputs, then turns them into a structured plan with category allocations and platform search links.</p>
  </div>
  <div class="grid-3">
    <article class="feature-card">
      <div class="icon">⌂</div><h3>Home Interior Planner</h3>
      <p>Choose rooms and quantities for lights, fans, furniture and dining pieces. Generate a budget-aware setup.</p>
      <a href="/register">Plan a home →</a>
    </article>
    <article class="feature-card">
      <div class="icon">✦</div><h3>Party Planner</h3>
      <p>Enter guests, event type, venue and needs for catering, decoration and entertainment.</p>
      <a href="/register">Plan a party →</a>
    </article>
    <article class="feature-card">
      <div class="icon">◇</div><h3>Jewelry Planner</h3>
      <p>Describe the occasion and style. Optionally upload an outfit image for visible color and style analysis.</p>
      <a href="/register">Plan jewelry →</a>
    </article>
  </div>
</section>

<section class="section soft">
  <div class="section-head"><span class="eyebrow">How it works</span><h2>From inputs to a usable plan.</h2></div>
  <div class="steps">
    <div><strong>01</strong><h3>Set the budget</h3><p>Start with a clear INR ceiling.</p></div>
    <div><strong>02</strong><h3>Add context</h3><p>Give the planner the quantities, guests, occasion or style information it needs.</p></div>
    <div><strong>03</strong><h3>Review the plan</h3><p>See allocations, estimated costs, suggestions and platform search links.</p></div>
  </div>
</section>

<section class="cta-band">
  <div><span class="eyebrow">Ready to optimize your budget?</span><h2>Build your first plan in a few clicks.</h2></div>
  <div class="hero-actions"><a class="btn light" href="/register">Create Account</a><a class="btn outline-light" href="/login">Sign In</a></div>
</section>
{% endblock %}
```

## `app/templates/jewelry_planner.html`

```html
{% extends "base.html" %}
{% block title %}Jewelry Budget Planner — PocketSmart AI{% endblock %}
{% block content %}
<section class="page-hero"><span class="eyebrow">Jewelry Budget Planner</span><h1>Match jewelry to the occasion and your budget.</h1><p>Add an outfit image for optional visible color/style analysis when Gemini is configured.</p></section>
<section class="section compact"><form class="planner-form" data-planner-form action="/generate-jewelry" method="post" enctype="multipart/form-data">
  <div class="form-section"><h2>① Budget Details</h2><label>Total Budget (₹)<input type="number" name="total_budget" min="1" step="1" required value="5000"></label></div>
  <div class="form-section"><h2>② Occasion & Preferences</h2><div class="grid-2"><label>Occasion<select name="occasion"><option>Birthday</option><option>Wedding</option><option>Party</option><option>Office</option><option>Festive</option><option>Date Night</option></select></label><label>Style Preferences<textarea name="preferences" rows="2" placeholder="e.g. minimal, gold tone, traditional"></textarea></label></div></div>
  <div class="form-section"><h2>③ Upload Outfit Image</h2><label class="upload-box"><input id="outfit-image" type="file" name="image" accept="image/png,image/jpeg,image/webp"><span>Choose JPG, PNG or WEBP (max {{ 5 }} MB)</span><img id="image-preview" class="image-preview" alt="Outfit preview" hidden></label></div>
  <button class="btn primary wide" type="submit">Get Recommendations</button><div class="loading" data-loading hidden>Analyzing your request…</div>
</form><div data-results class="result-slot"></div></section>
{% endblock %}
{% block scripts %}<script src="{{ url_for('static', path='js/planner.js') }}"></script>{% endblock %}
```

## `app/templates/jewelry_recommendations.html`

```html
{% extends "recommendations_details.html" %}
```

## `app/templates/login.html`

```html
{% extends "base.html" %}
{% block title %}Sign In — PocketSmart AI{% endblock %}
{% block content %}
<div class="auth-shell"><div class="auth-card">
  <div class="auth-brand">PocketSmart</div><div class="auth-subtitle">AI-Powered Budget Planning</div>
  <h1>Welcome back</h1>
  <form method="post" action="/login" class="form-stack">
    <label>Username<input name="username" required autocomplete="username" value="{{ form.username if form else '' }}" placeholder="Enter your username"></label>
    <label>Password<input type="password" name="password" required autocomplete="current-password" placeholder="Enter your password"></label>
    <button class="btn primary wide" type="submit">Sign In →</button>
  </form>
  <p class="auth-foot">Don’t have an account? <a href="/register">Create Account</a></p>
</div></div>
{% endblock %}
```

## `app/templates/partials/_recommendation_content.html`

```html
{% set result = recommendation.result %}
<div class="recommendation-head"><div><h2>Budget Summary</h2><p>{{ result.overview }}</p></div><div class="budget-metrics"><div><span>Total Budget</span><strong>₹{{ '%.2f'|format(result.total_budget) }}</strong></div><div><span>Allocated</span><strong>₹{{ '%.2f'|format(result.allocated_budget) }}</strong></div><div><span>Remaining</span><strong>₹{{ '%.2f'|format(result.remaining_budget) }}</strong></div></div></div>
{% if result.outfit_analysis %}<section class="result-section"><h2>Outfit Analysis</h2><div class="analysis-grid"><div><span>Colors</span><strong>{{ result.outfit_analysis.dominant_colors|join(', ') or 'Not available' }}</strong></div><div><span>Style</span><strong>{{ result.outfit_analysis.style or 'Not available' }}</strong></div><div><span>Formality</span><strong>{{ result.outfit_analysis.formality or 'Not available' }}</strong></div></div><p>{{ result.outfit_analysis.notes }}</p></section>{% endif %}
<section class="result-section"><h2>Recommendations</h2><div class="recommendation-list">{% for section in result.budget_breakdown %}
  <div class="category-section"><div class="category-title"><div><span class="pill">{{ section.category }}</span></div><div><strong>₹{{ '%.2f'|format(section.allocation) }}</strong><span>{{ '%.2f'|format(section.percentage_of_budget) }}%</span></div></div>
  {% for item in section["items"] %}<article class="recommendation-card"><div class="rec-main"><h3>{{ item.name }}</h3><p>{{ item.description }}</p><div class="rec-meta"><span>{{ item.platform }}</span><span>Qty: {{ item.quantity }}</span><span>Search: {{ item.search_terms }}</span></div><div class="shop-links">{% for platform, url in item.shopping_links.items() %}<a target="_blank" rel="noopener noreferrer" href="{{ url }}">Shop on {{ platform }} ↗</a>{% endfor %}</div></div><div class="rec-price">₹{{ '%.2f'|format(item.estimated_price) }}<small>estimated</small></div></article>{% endfor %}
  </div>{% endfor %}</div></section>
{% if result.styling_tips %}<section class="result-section"><h2>Styling Tips</h2><ul class="plain-list">{% for tip in result.styling_tips %}<li>{{ tip }}</li>{% endfor %}</ul></section>{% endif %}
{% if result.additional_suggestions %}<section class="result-section"><h2>Additional Suggestions</h2><ul class="plain-list">{% for tip in result.additional_suggestions %}<li>{{ tip }}</li>{% endfor %}</ul></section>{% endif %}
{% if result.warnings %}<div class="notice">{% for warning in result.warnings %}<div>{{ warning }}</div>{% endfor %}</div>{% endif %}
<div class="detail-actions"><a class="btn primary" href="/{{ recommendation.recommendation_type }}-planner">Create another plan</a><a class="btn secondary" href="/history">Back to history</a></div>
```

## `app/templates/party_planner.html`

```html
{% extends "base.html" %}
{% block title %}Party Budget Planner — PocketSmart AI{% endblock %}
{% block content %}
<section class="page-hero"><span class="eyebrow">Party Budget Planner</span><h1>Plan a great event without losing the budget.</h1><p>Set the guest count, event context and the services you actually need.</p></section>
<section class="section compact"><form class="planner-form" data-planner-form action="/generate-party" method="post">
  <div class="form-section"><h2>① Basic Information</h2><div class="grid-2"><label>Total Budget (₹)<input type="number" name="total_budget" min="1" step="1" required value="50000"></label><label>Number of Guests<input type="number" name="num_guests" min="1" required value="20"></label></div></div>
  <div class="form-section"><h2>② Event Details</h2><div class="grid-2"><label>Party Type<select name="party_type"><option>Birthday</option><option>Wedding</option><option>Corporate</option><option>Anniversary</option><option>Festival</option></select></label><label>Venue Type<select name="venue_type"><option>Home</option><option>Hall</option><option>Restaurant</option><option>Outdoor</option><option>Hotel</option></select></label></div></div>
  <div class="form-section"><h2>③ Party Needs</h2><div class="check-grid"><label class="check"><input type="checkbox" name="needs_catering" value="true" checked><span>Catering</span></label><label class="check"><input type="checkbox" name="needs_decoration" value="true" checked><span>Decoration</span></label><label class="check"><input type="checkbox" name="needs_entertainment" value="true"><span>Entertainment</span></label></div></div>
  <div class="form-section"><h2>④ Additional Requirements</h2><label>Special requests, theme, dietary needs, etc.<textarea name="additional_requirements" rows="4" placeholder="e.g. vegetarian menu, pastel theme, speaker setup"></textarea></label></div>
  <button class="btn primary wide" type="submit">Generate Budget Plan</button><div class="loading" data-loading hidden>Planning your event…</div>
</form><div data-results class="result-slot"></div></section>
{% endblock %}
{% block scripts %}<script src="{{ url_for('static', path='js/planner.js') }}"></script>{% endblock %}
```

## `app/templates/party_recommendations.html`

```html
{% extends "recommendations_details.html" %}
```

## `app/templates/recommendations_details.html`

```html
{% extends "base.html" %}
{% block title %}Recommendation Details — PocketSmart AI{% endblock %}
{% block content %}
<section class="page-hero"><span class="eyebrow">{{ recommendation.recommendation_type|title }} recommendation</span><h1>Your Personalized Plan</h1><p>{{ recommendation.created_at.strftime('%d %b %Y %H:%M') }}</p></section>
<section class="section compact">{% include 'partials/_recommendation_content.html' %}</section>
{% endblock %}
```

## `app/templates/register.html`

```html
{% extends "base.html" %}
{% block title %}Create Account — PocketSmart AI{% endblock %}
{% block content %}
<div class="auth-shell"><div class="auth-card">
  <div class="auth-brand">PocketSmart</div><div class="auth-subtitle">AI-Powered Budget Planning</div>
  <h1>Create your account</h1>
  <form method="post" action="/register" class="form-stack">
    <label>Username<input name="username" required autocomplete="username" value="{{ form.username if form else '' }}" placeholder="Choose a username"></label>
    <label>Email<input type="email" name="email" required autocomplete="email" value="{{ form.email if form else '' }}" placeholder="Enter your email"></label>
    <label>Password<input type="password" name="password" required minlength="8" autocomplete="new-password" placeholder="Create a strong password"></label>
    <label>Confirm Password<input type="password" name="confirm_password" required minlength="8" autocomplete="new-password" placeholder="Confirm your password"></label>
    <button class="btn primary wide" type="submit">Create Account →</button>
  </form>
  <p class="auth-foot">Already have an account? <a href="/login">Sign in</a></p>
</div></div>
{% endblock %}
```

## `app/templates/testimonials.html`

```html
{% extends "base.html" %}
{% block title %}Testimonials — PocketSmart AI{% endblock %}
{% block content %}
<section class="page-hero"><span class="eyebrow">User stories</span><h1>What users say</h1><p>Example testimonial content for the demo UI. Replace these entries with verified customer feedback before production use.</p></section>
<section class="section compact"><div class="grid-3">
  <article class="quote-card"><p>“PocketSmart made it easier to see how the same budget could be split across multiple home needs.”</p><strong>Demo user · Home planning</strong></article>
  <article class="quote-card"><p>“The party planner helped me turn a guest count and spending limit into a simple checklist.”</p><strong>Demo user · Event planning</strong></article>
  <article class="quote-card"><p>“The jewelry planner was useful for organizing style ideas around a fixed occasion budget.”</p><strong>Demo user · Jewelry planning</strong></article>
</div></section>
{% endblock %}
```

## `app/version.py`

```python
__version__ = "1.0.0"
```

## `data/.gitkeep`

```text

```

## `docker-compose.yml`

```yaml
services:
  pocketsmart:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    restart: unless-stopped
```

## `install.py`

```python
#!/usr/bin/env python3
"""Cross-platform PocketSmart AI installer.

Creates/updates the project's virtual environment, installs dependencies, and
prompts the user for the Gemini API key. The script intentionally stays in the
terminal at the end so it is convenient to run by double-clicking when Python
is configured to open .py files in a console.
"""
from __future__ import annotations

import os
import platform
import secrets
import subprocess
import sys
from getpass import getpass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
ENV_FILE = PROJECT_ROOT / ".env"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"


def say(message: str = "") -> None:
    print(message, flush=True)


def pause() -> None:
    try:
        input("\nPress Enter to close this installer... ")
    except (EOFError, KeyboardInterrupt):
        pass


def fail(message: str, exit_code: int = 1) -> None:
    say(f"\nERROR: {message}")
    pause()
    raise SystemExit(exit_code)


def run(command: list[str], *, cwd: Path | None = None) -> None:
    say(f"> {' '.join(command)}")
    completed = subprocess.run(command, cwd=str(cwd or PROJECT_ROOT), check=False)
    if completed.returncode != 0:
        fail(f"Command failed with exit code {completed.returncode}.")


def venv_python() -> Path:
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def upsert_env(values: dict[str, str]) -> None:
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    elif ENV_EXAMPLE.exists():
        lines = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    wanted = dict(values)
    found: set[str] = set()
    output: list[str] = []

    for raw in lines:
        stripped = raw.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in wanted:
                output.append(f"{key}={wanted[key]}")
                found.add(key)
                continue
        output.append(raw)

    if output and output[-1].strip():
        output.append("")

    for key, value in wanted.items():
        if key not in found:
            output.append(f"{key}={value}")

    ENV_FILE.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    say("=" * 70)
    say("PocketSmart AI - Installer")
    say("=" * 70)
    say(f"Operating system : {platform.system()} {platform.release()}")
    say(f"Python           : {platform.python_version()}")
    say(f"Project folder   : {PROJECT_ROOT}")

    if sys.version_info < (3, 10):
        fail("Python 3.10 or newer is required. Python 3.11 is recommended.")

    if not REQUIREMENTS.exists():
        fail("requirements.txt was not found. Run this installer from the project folder.")

    current = read_env()
    api_key = getpass("\nEnter your Gemini API key (leave blank to keep the existing key/use local fallback): ").strip()
    if not api_key:
        api_key = current.get("GEMINI_API_KEY", "")

    default_model = current.get("GEMINI_MODEL", "gemini-3.8-flash")

    say("\nGemini model examples:")
    say("  Latest     - gemini-3.8-flash")
    say("  Additional - gemini-3.7-flash")
    say("               gemini-3.6-flash")
    say("               gemini-3.5-flash")
    say("               gemini-3.5-flash-lite")
    say("               gemini-3.1-flash-lite")
    say("               gemini-2.5-flash")
    say("               gemini-2.5-flash-lite")
    say("  Enter any model ID supported by your Gemini API key.")

    model = input(
        f"Gemini model [{default_model}]: "
    ).strip() or default_model

    secret_key = current.get("SECRET_KEY", "").strip()
    if not secret_key or secret_key == "replace-this-with-a-long-random-secret":
        secret_key = secrets.token_urlsafe(48)
        say("Generated a new SECRET_KEY for this installation.")

    say("\n[1/4] Creating/updating Python virtual environment...")
    if not (PROJECT_ROOT / ".venv").exists():
        run([sys.executable, "-m", "venv", ".venv"])
    else:
        say("Virtual environment already exists; keeping it.")

    py = venv_python()
    if not py.exists():
        fail(f"Virtual environment Python executable was not found at: {py}")

    say("\n[2/4] Upgrading pip...")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])

    say("\n[3/4] Installing project dependencies...")
    run([str(py), "-m", "pip", "install", "-r", str(REQUIREMENTS)])

    say("\n[4/4] Writing .env configuration...")
    upsert_env(
        {
            "SECRET_KEY": secret_key,
            "GEMINI_API_KEY": api_key,
            "GEMINI_MODEL": model,
        }
    )

    say("\n" + "=" * 70)
    say("Installation complete!")
    say("=" * 70)
    say(f"Environment : {ENV_FILE}")
    say(f"Model       : {model}")
    say(f"API key     : {'configured' if api_key else 'not configured (local fallback enabled)'}")
    say("\nTo launch PocketSmart AI, run:")
    if os.name == "nt":
        say("  python launch.py")
    else:
        say("  python3 launch.py")
    say("\nThe launcher will start the server, keep this terminal open, and open your browser automatically.")
    pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        say("\nInstallation cancelled.")
        pause()
```

## `launch.py`

```python
#!/usr/bin/env python3
"""Cross-platform PocketSmart AI launcher.

Starts Uvicorn using the project's virtual-environment Python, waits for the
health endpoint, opens the browser, and keeps the terminal attached to the
server until the user stops it with Ctrl+C.

Model selection examples:
    python launch.py --list-models
    python launch.py --model gemini-3.8-flash
    python launch.py --model gemini-3.5-flash-lite

The --model option overrides GEMINI_MODEL for this launch only. It does not
modify .env.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
HOST = os.getenv("POCKETSMART_HOST", "127.0.0.1")
PORT = int(os.getenv("POCKETSMART_PORT", "8000"))
URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{URL}/health"

# These are examples of Gemini models suitable for PocketSmart-style text and
# multimodal recommendation workloads. Availability is account/region/API
# dependent; use `python launch.py --list-models` to see the examples and
# consult Google's current model catalog for your account's actual access.
MODEL_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("gemini-3.8-flash", "Current stable flagship Flash model."),
    ("gemini-3.7-flash", "Previous-generation stable Flash model."),
    ("gemini-3.6-flash", "Stable Flash model balancing speed and multimodal capability."),
    ("gemini-3.5-flash", "Legacy stable Flash model for routine workloads."),
    ("gemini-3.5-flash-lite", "Fast, cost-efficient Flash-Lite model."),
    ("gemini-3.1-flash-lite", "Efficient Flash-Lite model for lightweight workloads."),
    ("gemini-flash-latest", "Alias for the latest Gemini Flash release."),
    ("gemini-flash-lite-latest", "Alias for the latest Gemini Flash-Lite release."),
    ("gemini-2.5-flash", "Older stable Flash model; API access may be limited."),
    ("gemini-2.5-flash-lite", "Older stable Flash-Lite model; API access may be limited."),
)


def say(message: str = "") -> None:
    print(message, flush=True)


def pause() -> None:
    try:
        input("\nPress Enter to close this launcher... ")
    except (EOFError, KeyboardInterrupt):
        pass


def venv_python() -> Path:
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def current_model_from_env() -> str:
    """Read GEMINI_MODEL from .env for display without importing the app."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return "gemini-3.8-flash"

    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "GEMINI_MODEL":
            return value.strip().strip('"').strip("'") or "gemini-3.8-flash"

    return "gemini-3.8-flash"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch the PocketSmart AI web server."
    )
    parser.add_argument(
        "--model",
        help="Override GEMINI_MODEL for this launch only.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Show example Gemini model IDs and exit.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the server without opening a browser automatically.",
    )
    return parser.parse_args()


def print_model_examples() -> None:
    say("\nPocketSmart AI Gemini model examples")
    say("=" * 70)
    for model, description in MODEL_EXAMPLES:
        say(f"  {model:<28} {description}")
    say("=" * 70)
    say("These are examples, not a guarantee that every model is enabled for every key.")
    say("Check Google's current Gemini model catalog or use your account's model listing.")


def wait_for_server(timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1.5) as response:
                return 200 <= response.status < 300
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.5)
    return False


def main() -> None:
    args = parse_args()

    if args.list_models:
        print_model_examples()
        pause()
        return

    say("=" * 70)
    say("PocketSmart AI - Launcher")
    say("=" * 70)
    say(f"Project : {PROJECT_ROOT}")
    say(f"Web app : {URL}")

    configured_model = current_model_from_env()
    selected_model = args.model.strip() if args.model else configured_model

    say(f"Gemini model: {selected_model}")

    if args.model:
        say("Model override: command line (does not modify .env)")

    py = venv_python()
    if not py.exists():
        say("\nPocketSmart AI is not installed yet.")
        say("Run the installer first:")
        say(f"  {sys.executable} install.py")
        pause()
        return

    command = [
        str(py),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
    ]

    child_env = os.environ.copy()
    child_env["GEMINI_MODEL"] = selected_model

    say("\nStarting PocketSmart AI server...")
    say("The server output will remain visible in this terminal.")
    say("Press Ctrl+C to stop PocketSmart AI.\n")

    process = subprocess.Popen(
        command,
        cwd=str(PROJECT_ROOT),
        env=child_env,
    )

    try:
        if wait_for_server():
            say(f"\nServer is ready: {URL}")
            if not args.no_browser:
                say("Opening your default web browser...")
                webbrowser.open(URL, new=2)
            else:
                say("Browser launch disabled (--no-browser).")
        else:
            say("\nThe server did not report healthy within 30 seconds.")
            say(f"Try opening {URL} manually if Uvicorn is still starting.")

        return_code = process.wait()
        say(f"\nPocketSmart AI server stopped (exit code {return_code}).")
    except KeyboardInterrupt:
        say("\nStopping PocketSmart AI...")
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        say("PocketSmart AI has been stopped.")
    finally:
        pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pause()
```

## `main.py`

```python
"""Convenience entry point for PocketSmart AI.

Run with: python main.py
Or use: uvicorn app.main:app --reload
"""

import uvicorn

from app.main import app


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
```

## `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

## `requirements.txt`

```text
fastapi>=0.128,<1
uvicorn[standard]>=0.40,<1
sqlalchemy>=2.0,<3
pydantic>=2.13,<3
jinja2>=3.1,<4
itsdangerous>=2.2,<3
python-multipart>=0.0.20,<1
python-dotenv>=1.0,<2
PyJWT>=2.10,<3
httpx>=0.28,<1
Pillow>=11,<13
google-genai>=1.50,<2
pytest>=8,<9
```

## `scripts/check_gemini.py`

```python
from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Gemini text or multimodal connectivity")
    parser.add_argument("--image", type=Path, help="Optional local image to include in the prompt")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    if not api_key:
        print("GEMINI_API_KEY is not set. Configure .env first.")
        return 1

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("google-genai is not installed. Run: pip install -r requirements.txt")
        return 1

    client = genai.Client(api_key=api_key)
    prompt = "Reply with exactly one sentence confirming that PocketSmart AI Gemini connectivity works."
    contents: list[object] = [prompt]

    if args.image:
        if not args.image.exists():
            print(f"Image not found: {args.image}")
            return 1
        mime = "image/jpeg"
        suffix = args.image.suffix.lower()
        if suffix == ".png":
            mime = "image/png"
        elif suffix == ".webp":
            mime = "image/webp"
        contents.append(types.Part.from_bytes(data=args.image.read_bytes(), mime_type=mime))
        contents.append("Briefly describe only the visible colors and clothing style in this outfit image.")

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=200),
    )
    print(response.text or "No text returned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## `scripts/diagnose_gemini.py`

```python
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
load_dotenv(ENV_FILE, override=True)


def masked(value: str) -> str:
    value = value.strip()
    if not value:
        return "NOT SET"
    if len(value) <= 10:
        return "SET (short key)"
    return f"{value[:5]}...{value[-4:]}"


def main() -> int:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    print(f"Project root : {ROOT}")
    print(f".env path    : {ENV_FILE}")
    print(f".env exists  : {ENV_FILE.exists()}")
    print(f"API key      : {masked(key)}")
    print(f"Model        : {model}")

    if not key:
        print("\nERROR: GEMINI_API_KEY is not loaded from .env.")
        return 1

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        print(f"\nERROR: google-genai is not installed: {exc}")
        print("Run: python -m pip install -U google-genai")
        return 1

    try:
        import google.genai
        print(f"google-genai : {getattr(google.genai, '__version__', 'unknown')}")
    except Exception:
        pass

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: POCKETSMART_GEMINI_OK",
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=50,
            ),
        )
        print("\nGemini API call: SUCCESS")
        print("Response:", (response.text or "").strip())
        return 0
    except Exception as exc:
        print("\nGemini API call: FAILED")
        print(f"{type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

## `scripts/smoke_test.py`

```python
from __future__ import annotations

import sys
import urllib.request


def main() -> int:
    base = "http://127.0.0.1:8000"
    for path in ("/health", "/startup", "/docs"):
        with urllib.request.urlopen(base + path, timeout=5) as response:
            print(path, response.status)
    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## `tests/conftest.py`

```python
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import os
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pocketsmart-123456")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/test_pocketsmart.db")

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
```

## `tests/test_auth.py`

```python
def test_register_login_and_protected_page(client):
    response = client.post("/register", follow_redirects=False, data={
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "Welcome, demo_user" in dashboard.text

    logout = client.get("/logout", follow_redirects=False)
    assert logout.status_code == 303
    blocked = client.get("/dashboard")
    assert blocked.status_code in (303, 401)


def test_token_endpoint(client):
    client.post("/register", data={
        "username": "token_user",
        "email": "token@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    response = client.post("/token", data={"username": "token_user", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
```

## `tests/test_brand_navigation.py`

```python
from fastapi.testclient import TestClient


def test_logo_points_to_dashboard_when_authenticated(client: TestClient):
    with client:
        register = client.post(
            "/register",
            data={
                "username": "logotest",
                "email": "logo@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            follow_redirects=False,
        )
        assert register.status_code == 303
        response = client.get("/", follow_redirects=False)

    assert response.status_code == 200
    assert 'class="brand" href="/dashboard"' in response.text
    assert '>Logout<' in response.text
```

## `tests/test_gemini_budget.py`

```python
from app.services.gemini_utils import _post_process


def test_gemini_budget_is_normalized_to_user_budget():
    data = {
        "total_budget": 62000,
        "allocated_budget": 62000,
        "remaining_budget": 0,
        "overview": "test",
        "budget_breakdown": [
            {
                "category": "Lighting",
                "allocation": 40000,
                "percentage_of_budget": 64,
                "items": [
                    {
                        "name": "Light A",
                        "description": "test",
                        "estimated_price": 20000,
                        "quantity": 2,
                        "platform": "Amazon",
                        "search_terms": "light A",
                        "shopping_links": {},
                    }
                ],
            },
            {
                "category": "Furniture",
                "allocation": 22000,
                "percentage_of_budget": 36,
                "items": [
                    {
                        "name": "Chair",
                        "description": "test",
                        "estimated_price": 11000,
                        "quantity": 2,
                        "platform": "Flipkart",
                        "search_terms": "chair",
                        "shopping_links": {},
                    }
                ],
            },
        ],
        "outfit_analysis": None,
        "styling_tips": [],
        "additional_suggestions": [],
        "source": "gemini",
        "warnings": [],
    }

    result = _post_process(data, {}, requested_budget=50000)

    assert result["total_budget"] == 50000
    assert result["allocated_budget"] <= 50000
    assert result["remaining_budget"] >= 0
    assert any("normalized it to the user's budget" in w for w in result["warnings"])
    assert any("exceeded the user's budget" in w for w in result["warnings"])


def test_gemini_compact_json_is_normalized_instead_of_rejected():
    data = {
        "total_budget": 5000,
        "remaining_budget": 500,
        "recommendations": [
            {
                "category": "Jewelry",
                "name": "Stud earrings",
                "description": "Simple studs",
                "price": 4500,
                "quantity": 1,
                "platform": "Amazon",
            }
        ],
    }
    fallback = {
        "overview": "fallback",
        "budget_breakdown": [],
        "outfit_analysis": None,
        "styling_tips": [],
        "additional_suggestions": [],
    }

    result = _post_process(data, fallback, requested_budget=5000)

    assert result["total_budget"] == 5000
    assert result["allocated_budget"] == 4500
    assert result["remaining_budget"] == 500
    assert result["budget_breakdown"][0]["items"][0]["estimated_price"] == 4500


def test_gemini_minimal_json_gets_safe_defaults():
    data = {"total_budget": 50000, "remaining_budget": 50000}
    fallback = {
        "overview": "starter",
        "budget_breakdown": [],
        "outfit_analysis": None,
        "styling_tips": [],
        "additional_suggestions": [],
    }

    result = _post_process(data, fallback, requested_budget=50000)

    assert result["total_budget"] == 50000
    assert result["allocated_budget"] == 0
    assert result["remaining_budget"] == 50000
    assert any("incomplete recommendation structure" in w for w in result["warnings"])



def test_gemini_malformed_json_with_trailing_comma_can_be_repaired():
    from app.services.gemini_utils import _safe_json

    raw = """
    {
      "total_budget": 50000,
      "overview": "Test plan",
      "budget_breakdown": [],
    }
    """

    result = _safe_json(raw)
    assert result["total_budget"] == 50000
    assert result["budget_breakdown"] == []


def test_string_outfit_analysis_is_normalized_to_notes():
    data = {
        "total_budget": 5000,
        "recommendations": [
            {
                "category": "Jewelry",
                "name": "Stud earrings",
                "description": "Simple studs",
                "price": 1200,
                "quantity": 1,
                "platform": "Amazon",
            }
        ],
        "outfit_analysis": "The outfit is a festive modern celebratory look.",
    }
    fallback = {
        "overview": "fallback",
        "budget_breakdown": [],
        "outfit_analysis": None,
        "styling_tips": [],
        "additional_suggestions": [],
    }

    result = _post_process(data, fallback, requested_budget=5000)

    assert result["outfit_analysis"]["notes"] == "The outfit is a festive modern celebratory look."


def test_safe_json_repairs_unquoted_keys_and_trailing_commas():
    from app.services.gemini_utils import _safe_json

    raw = '''
    {
      total_budget: 5000,
      overview: "Test",
      budget_breakdown: [],
    }
    '''

    result = _safe_json(raw)
    assert result["total_budget"] == 5000
    assert result["overview"] == "Test"


def test_safe_json_handles_code_fence():
    from app.services.gemini_utils import _safe_json

    raw = '''```json
    {
      "total_budget": 5000,
      "budget_breakdown": []
    }
    ```'''

    result = _safe_json(raw)
    assert result["total_budget"] == 5000
```

## `tests/test_health.py`

```python
def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
```

## `tests/test_planners.py`

```python
def register(client):
    client.post("/register", data={
        "username": "planner_user",
        "email": "planner@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })


def test_home_planner_fallback(client):
    register(client)
    response = client.post("/generate-home", headers={"Accept": "application/json"}, data={
        "total_budget": 50000,
        "num_lights": 4,
        "num_fans": 2,
        "num_furniture": 2,
        "num_dining_tables": 1,
        "rooms": ["Living Room", "Bedroom"],
        "additional_requirements": "minimal",
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "home"
    assert payload["result"]["remaining_budget"] >= 0
    assert payload["result"]["source"] == "fallback"


def test_party_planner_fallback(client):
    register(client)
    response = client.post("/generate-party", headers={"Accept": "application/json"}, data={
        "total_budget": 50000,
        "num_guests": 20,
        "party_type": "Birthday",
        "venue_type": "Home",
        "needs_catering": "true",
        "needs_decoration": "true",
        "needs_entertainment": "false",
        "additional_requirements": "vegetarian",
    })
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["remaining_budget"] >= 0


def test_jewelry_planner_fallback_without_image(client):
    register(client)
    response = client.post("/generate-jewelry", headers={"Accept": "application/json"}, data={
        "total_budget": 5000,
        "occasion": "Birthday",
        "preferences": "minimal and gold tone",
    })
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["source"] == "fallback"
    assert result["outfit_analysis"]["style"] == "Not analyzed"


def test_jewelry_image_upload_is_accepted(client):
    from io import BytesIO
    from PIL import Image

    register(client)
    buffer = BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, format="PNG")
    buffer.seek(0)
    response = client.post("/generate-jewelry", headers={"Accept": "application/json"}, data={
        "total_budget": 5000,
        "occasion": "Birthday",
        "preferences": "minimal",
    }, files={"image": ("outfit.png", buffer, "image/png")})
    assert response.status_code == 200
    assert response.json()["type"] == "jewelry"


def test_jewelry_invalid_image_is_rejected(client):
    register(client)
    response = client.post("/generate-jewelry", data={
        "total_budget": 5000,
        "occasion": "Birthday",
        "preferences": "minimal",
    }, files={"image": ("outfit.txt", b"not an image", "text/plain")})
    assert response.status_code == 400
    assert "Only JPG" in response.json()["detail"]
```

## `tests/test_session_and_history.py`

```python
def register(client):
    client.post("/register", data={
        "username": "history_user",
        "email": "history@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })


def test_session_info_and_history(client):
    register(client)
    info = client.get("/session-info")
    assert info.status_code == 200
    assert info.json()["username"] == "history_user"

    client.post("/generate-home", headers={"Accept": "application/json"}, data={"total_budget": 20000})
    history = client.get("/history")
    assert history.status_code == 200
    assert "Home Budget" in history.text

    detail = client.get("/recommendations-details/1")
    assert detail.status_code == 200
    assert "Budget Summary" in detail.text

    updated = client.post("/session-data", json={"data": {"preferred_theme": "minimal"}})
    assert updated.status_code == 200
    assert updated.json()["data"]["preferred_theme"] == "minimal"
```

