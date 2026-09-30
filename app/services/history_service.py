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
