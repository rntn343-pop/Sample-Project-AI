def register(client):
    client.post("/register", data={
        "username": "history_user",
        "email": "history@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })


def test_session_info_and_history(client):
    register(client)
    info = client.get("/session-info")
    assert info.status_code == 200
    assert info.json()["username"] == "history_user"

    client.post("/generate-home", headers={"Accept": "application/json"}, data={"total_budget": 20000})
    history = client.get("/history")
    assert history.status_code == 200
    assert "Home Budget" in history.text

    detail = client.get("/recommendations-details/1")
    assert detail.status_code == 200
    assert "Budget Summary" in detail.text

    updated = client.post("/session-data", json={"data": {"preferred_theme": "minimal"}})
    assert updated.status_code == 200
    assert updated.json()["data"]["preferred_theme"] == "minimal"
