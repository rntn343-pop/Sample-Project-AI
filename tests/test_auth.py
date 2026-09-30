def test_register_login_and_protected_page(client):
    response = client.post("/register", follow_redirects=False, data={
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "Welcome, demo_user" in dashboard.text

    logout = client.get("/logout", follow_redirects=False)
    assert logout.status_code == 303
    blocked = client.get("/dashboard")
    assert blocked.status_code in (303, 401)


def test_token_endpoint(client):
    client.post("/register", data={
        "username": "token_user",
        "email": "token@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    response = client.post("/token", data={"username": "token_user", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
