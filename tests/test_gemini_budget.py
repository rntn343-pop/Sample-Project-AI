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
