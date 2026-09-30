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
                + [f"Gemini error: {type(exc).__name__}: {str(exc)[:500]}. Local fallback used because GEMINI_FALLBACK_ON_ERROR=true."]
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
and Amazon/Flipkart for decor where useful.
Keep the complete plan within the total budget. The total_budget field must equal the submitted budget exactly.
The sum of every estimated_price * quantity across every budget_breakdown item must be <= the submitted budget.
If the requested services cannot all fit, reduce quantities or omit optional items. Never invent a cheaper unit price just to make the arithmetic fit.
Provide search terms instead of direct URLs.
Do not wrap the JSON in markdown code fences. Do not add comments or trailing commas.
Return exactly these top-level fields: total_budget, allocated_budget, remaining_budget, overview,
budget_breakdown, outfit_analysis, styling_tips, additional_suggestions, source, warnings.
`budget_breakdown` must be a list of objects containing category, allocation, percentage_of_budget, and items.
Each item must contain name, description, estimated_price, quantity, platform, search_terms, and shopping_links.
Use an empty object for shopping_links and null for outfit_analysis when it is not applicable.
Return JSON matching this example shape:
{_schema_hint()}
""".strip()
    return _generate(prompt, party_fallback(budget), requested_budget=budget)


def generate_jewelry_recommendations(
    data: dict[str, Any],
    image_bytes: bytes | None,
    mime_type: str | None,
) -> dict[str, Any]:
    budget = float(data["total_budget"])
    image_instruction = (
        "An outfit image has been supplied. Analyze only visible colors, style cues, and formality."
        if image_bytes and mime_type
        else "No outfit image was supplied, so set outfit_analysis to null."
    )
    prompt = f"""
Create a jewelry recommendation plan for India.
Total budget: INR {budget:.2f}
Occasion: {data.get('occasion', '')}
Style preferences: {data.get('preferences') or 'None'}
{image_instruction}
Analyze an image only for visible colors, style cues, and formality; do not identify the person and do not infer sensitive traits.
Recommend jewelry that fits the budget. The total_budget field must equal the submitted budget exactly.
The sum of every estimated_price * quantity across every budget_breakdown item must be <= the submitted budget.
Do not increase the budget to accommodate a preferred item. Never invent a cheaper unit price just to make the arithmetic fit.
Favor Amazon and Flipkart search terms; Myntra may be used for fashion accessories. Return no direct URLs.
Do not wrap the JSON in markdown code fences. Do not add comments or trailing commas.
Return exactly these top-level fields: total_budget, allocated_budget, remaining_budget, overview,
budget_breakdown, outfit_analysis, styling_tips, additional_suggestions, source, warnings.
`budget_breakdown` must be a list of objects containing category, allocation, percentage_of_budget, and items.
Each item must contain name, description, estimated_price, quantity, platform, search_terms, and shopping_links.
`outfit_analysis` must be either null or an object containing dominant_colors (array), style, formality, and notes.
Return JSON matching this example shape:
{_schema_hint()}
""".strip()
    return _generate(
        prompt,
        jewelry_fallback(budget),
        image_bytes=image_bytes,
        mime_type=mime_type,
        requested_budget=budget,
    )
