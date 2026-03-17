from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_ping_returns_pong():
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"pong": True}


def test_landing_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_landing_contains_welcome_message():
    response = client.get("/")
    assert "Welcome!" in response.text


def test_landing_contains_current_time():
    response = client.get("/")
    assert "Current Server Time" in response.text
    assert "UTC" in response.text


def test_landing_includes_tailwind():
    response = client.get("/")
    assert "tailwindcss" in response.text


def test_contact_page_returns_html():
    response = client.get("/contact")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_contact_page_contains_form():
    response = client.get("/contact")
    assert "Contact Us" in response.text
    assert 'name="name"' in response.text
    assert 'name="email"' in response.text
    assert 'name="message"' in response.text
    assert 'action="/api/contact"' in response.text


def test_contact_page_dark_theme():
    response = client.get("/contact")
    assert "bg-gray-900" in response.text


def test_contact_submit():
    response = client.post(
        "/api/contact",
        data={"name": "Alice", "email": "alice@example.com", "message": "Hello!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["message"] == "Hello!"


def test_about_returns_html():
    response = client.get("/about")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_about_contains_project_info():
    response = client.get("/about")
    assert "CSymphony Demo" in response.text
    assert "v0.1.0" in response.text


def test_about_has_dark_theme():
    response = client.get("/about")
    assert "bg-gray-950" in response.text


def test_404_returns_html():
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]


def test_404_contains_friendly_message():
    response = client.get("/nonexistent")
    assert "404" in response.text
    assert "Page not found" in response.text


def test_404_has_dark_theme():
    response = client.get("/nonexistent")
    assert "bg-gray-950" in response.text


def test_404_has_home_link():
    response = client.get("/nonexistent")
    assert 'href="/"' in response.text
