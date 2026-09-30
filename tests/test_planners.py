def register(client):
    client.post("/register", data={
        "username": "planner_user",
        "email": "planner@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })


def test_home_planner_fallback(client):
    register(client)
    response = client.post("/generate-home", headers={"Accept": "application/json"}, data={
        "total_budget": 50000,
        "num_lights": 4,
        "num_fans": 2,
        "num_furniture": 2,
        "num_dining_tables": 1,
        "rooms": ["Living Room", "Bedroom"],
        "additional_requirements": "minimal",
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "home"
    assert payload["result"]["remaining_budget"] >= 0
    assert payload["result"]["source"] == "fallback"


def test_party_planner_fallback(client):
    register(client)
    response = client.post("/generate-party", headers={"Accept": "application/json"}, data={
        "total_budget": 50000,
        "num_guests": 20,
        "party_type": "Birthday",
        "venue_type": "Home",
        "needs_catering": "true",
        "needs_decoration": "true",
        "needs_entertainment": "false",
        "additional_requirements": "vegetarian",
    })
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["remaining_budget"] >= 0


def test_jewelry_planner_fallback_without_image(client):
    register(client)
    response = client.post("/generate-jewelry", headers={"Accept": "application/json"}, data={
        "total_budget": 5000,
        "occasion": "Birthday",
        "preferences": "minimal and gold tone",
    })
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["source"] == "fallback"
    assert result["outfit_analysis"]["style"] == "Not analyzed"


def test_jewelry_image_upload_is_accepted(client):
    from io import BytesIO
    from PIL import Image

    register(client)
    buffer = BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, format="PNG")
    buffer.seek(0)
    response = client.post("/generate-jewelry", headers={"Accept": "application/json"}, data={
        "total_budget": 5000,
        "occasion": "Birthday",
        "preferences": "minimal",
    }, files={"image": ("outfit.png", buffer, "image/png")})
    assert response.status_code == 200
    assert response.json()["type"] == "jewelry"


def test_jewelry_invalid_image_is_rejected(client):
    register(client)
    response = client.post("/generate-jewelry", data={
        "total_budget": 5000,
        "occasion": "Birthday",
        "preferences": "minimal",
    }, files={"image": ("outfit.txt", b"not an image", "text/plain")})
    assert response.status_code == 400
    assert "Only JPG" in response.json()["detail"]
