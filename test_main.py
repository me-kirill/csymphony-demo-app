from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_ping_returns_pong():
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"pong": True}


def test_stats_returns_expected_fields():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "uptime" in data
    assert "uptime_seconds" in data
    assert "memory_mb" in data
    assert "requests_served" in data
    assert isinstance(data["memory_mb"], float)
    assert data["uptime_seconds"] >= 0
    assert data["requests_served"] >= 1


def test_dashboard_returns_html():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "System Dashboard" in response.text
    assert "/api/stats" in response.text
