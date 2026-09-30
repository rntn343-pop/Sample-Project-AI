from fastapi.testclient import TestClient


def test_logo_points_to_dashboard_when_authenticated(client: TestClient):
    with client:
        register = client.post(
            "/register",
            data={
                "username": "logotest",
                "email": "logo@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            follow_redirects=False,
        )
        assert register.status_code == 303
        response = client.get("/", follow_redirects=False)

    assert response.status_code == 200
    assert 'class="brand" href="/dashboard"' in response.text
    assert '>Logout<' in response.text
