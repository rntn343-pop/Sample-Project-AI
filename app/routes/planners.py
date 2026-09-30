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