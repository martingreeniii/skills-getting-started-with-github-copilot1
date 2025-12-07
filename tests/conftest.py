import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activity_data(client):
    """Fixture to fetch current activities from the app"""
    response = client.get("/activities")
    return response.json()
