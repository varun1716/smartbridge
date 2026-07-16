import pytest
from fastapi.testclient import TestClient
import unittest.mock as mock
import os

# Set fallback AI provider for unit tests so they run instantly without API calls
os.environ["AI_PROVIDER"] = "fallback"

from backend.main import app
from backend import database

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup: Ensure DB is clean/initialized
    database.init_db()
    yield
    # Teardown: If we wanted to delete the db file, we could do it here.
    # But since it's just SQLite, keeping it or leaving it is fine.

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_generate_starters():
    payload = {
        "event_description": "AI for Sustainable Cities Panel Discussion",
        "interests": ["climate change", "urban planning"]
    }
    response = client.post("/api/generate-starters", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert len(data["extracted_themes"]) > 0
    assert len(data["conversation_starters"]) == 3
    assert data["event_description"] == payload["event_description"]

def test_feedback():
    # Insert a sample interaction first
    interaction_id = database.save_interaction(
        event_description="Test Event",
        interests=["interest1"],
        extracted_themes=["theme1"],
        conversation_starters=["starter1"]
    )
    
    payload = {
        "interaction_id": interaction_id,
        "feedback": "thumbs_up"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["feedback"] == "thumbs_up"
    
    # Verify in DB
    history = database.get_history()
    matched = [h for h in history if h["id"] == interaction_id]
    assert len(matched) == 1
    assert matched[0]["feedback"] == "thumbs_up"

def test_history():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@mock.patch("backend.wikipedia_service.requests.get")
def test_fact_check(mock_get):
    # Mock Wikipedia API response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    
    # First mock return for search, second mock return for page extract
    mock_response.json.side_effect = [
        {
            "query": {
                "search": [
                    {"title": "Blockchain in healthcare"}
                ]
            }
        },
        {
            "query": {
                "pages": {
                    "12345": {
                        "extract": "Blockchain in healthcare is a technology that allows medical data to be recorded securely."
                    }
                }
            }
        }
    ]
    mock_get.return_value = mock_response
    
    response = client.get("/api/fact-check?query=blockchain in healthcare")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert "Blockchain" in data["topic"]
    assert "medical data" in data["summary"]
    assert "wikipedia.org" in data["source_url"]
