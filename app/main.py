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