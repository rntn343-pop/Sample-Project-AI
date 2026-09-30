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
