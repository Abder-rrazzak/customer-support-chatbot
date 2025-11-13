import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post("/chat", json={
        "message": "Hello",
        "session_id": "test_session"
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "intent" in data
    assert "confidence" in data