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
