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
