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