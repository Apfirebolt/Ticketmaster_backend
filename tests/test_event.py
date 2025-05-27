import pytest
from fastapi.testclient import TestClient
import sys
import os
import random

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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


created_event_id = None


def test_create_event(auth_token):
    global created_event_id
    response = client.post(
        "/api/events/",
        json={
            "id": random.randint(1, 100000),  # Random ID for testing
            "name": "New Event",
            "description": "This is a sample event for testing.",
            "start_time": "2025-06-01T18:00:00",
            "start_date": "2025-06-01",
            "location": "New Venue",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    created_event_id = data["id"]


def test_list_event_unauthenticated():
    response = client.get("/api/events/")
    assert response.status_code == 401  # Unauthorized access should return 401
    assert response.json() == {"detail": "Not authenticated"}  # Check the error message


def test_get_event_list(auth_token):
    response = client.get(
        "/api/events/", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Ensure the response is a list
    if data:  # If there are events, check the first one
        assert "id" in data[0]
        assert "name" in data[0]
        assert "description" in data[0]
        assert "start_time" in data[0]
        assert "start_date" in data[0]
        assert "location" in data[0]


def test_get_event_by_id(auth_token):
    global created_event_id
    # Ensure an event was actually created before attempting to get it by ID
    assert created_event_id is not None, "No event ID was created to retrieve."

    response = client.get(
        f"/api/events/{created_event_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_event_id
    assert "name" in data
    assert "description" in data
    assert "start_time" in data
    assert "start_date" in data
    assert "location" in data


# test update event
def test_update_event(auth_token):
    global created_event_id
    # Ensure an event was actually created before attempting to update
    assert created_event_id is not None, "No event ID was created to update."

    response = client.put(
        f"/api/events/{created_event_id}",
        json={
            "name": "Updated Event",
            "description": "This is an updated description.",
            "start_time": "2025-06-02T18:00:00",
            "start_date": "2025-06-02",
            "location": "Updated Venue",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_event_id
    assert data["name"] == "Updated Event"
    assert data["description"] == "This is an updated description."


# Add this new test function to delete the event
def test_delete_event(auth_token):
    global created_event_id
    # Ensure an event was actually created before attempting to delete
    assert created_event_id is not None, "No event ID was created to delete."

    response = client.delete(
        f"/api/events/{created_event_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204
