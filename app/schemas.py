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