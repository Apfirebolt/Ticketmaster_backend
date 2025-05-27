from fastapi.testclient import TestClient
import sys
import os

# Get the absolute path to the project's root directory (one level up from the 'tests' folder)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI Ticket Master App!"}
