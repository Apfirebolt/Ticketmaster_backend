from fastapi.testclient import TestClient
import sys
import os
import pytest

# Get the absolute path to the project's root directory (one level up from the 'tests' folder)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app


client = TestClient(app)


@pytest.fixture(scope="module")
def auth_token():
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "pass123"}
    )
    assert response.status_code == 200
    return response.json().get("access_token") or response.json().get("token")


def test_register():
    response = client.post(
        "/api/auth/register",
        json={
            "username": "test",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 400


def test_login():
    # Ensure the user exists (register if needed)
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "pass123"}
    )
    # print error response if login fails
    if response.status_code != 200:
        print("Login failed:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data or "token" in data


def test_invalid_login_empty_fields():
    response = client.post("/api/auth/login", json={"email": "", "password": ""})
    assert response.status_code == 400 or response.status_code == 422


def test_invalid_login_wrong_password():
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "wrongpass"}
    )
    assert response.status_code == 401 or response.status_code == 400


def test_register_missing_fields():
    response = client.post(
        "/api/auth/register",
        json={
            "username": "",
            "email": "",
            "password": "",
        },
    )
    assert response.status_code == 422 or response.status_code == 400


def test_register_invalid_email():
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "not-an-email",
            "password": "password123",
        },
    )
    assert response.status_code == 422 or response.status_code == 400


def test_get_profile_no_token():
    response = client.get("/api/auth/profile")
    assert response.status_code == 401


def test_get_profile_invalid_token():
    response = client.get(
        "/api/auth/profile", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


def test_get_all_users(auth_token):
    response = client.get("/api/auth", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Ensure the response is a list
    # Example: check that each user has id, username, and email fields
    for user in data:
        assert "id" in user
        assert "username" in user
        assert "email" in user
