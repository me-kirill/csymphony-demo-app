from fastapi.testclient import TestClient

from main import THEMES, app

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


def test_nav_present_on_all_pages():
    for path in ["/", "/about", "/contact", "/dashboard"]:
        response = client.get(path)
        assert "<nav" in response.text, f"nav missing on {path}"
        assert 'href="/' in response.text, f"Home link missing on {path}"
        assert "/dashboard" in response.text, f"Dashboard link missing on {path}"
        assert "/about" in response.text, f"About link missing on {path}"
        assert "/contact" in response.text, f"Contact link missing on {path}"


def test_nav_highlights_current_page():
    response = client.get("/about")
    assert "font-semibold" in response.text


def test_theme_switcher_present_on_all_pages():
    for path in ["/", "/about", "/contact", "/dashboard"]:
        response = client.get(path)
        assert "Theme" in response.text, f"theme switcher missing on {path}"


def test_all_themes_load_on_all_pages():
    for theme_id in THEMES:
        for path in ["/", "/about", "/contact", "/dashboard"]:
            response = client.get(f"{path}?theme={theme_id}")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]


def test_theme_changes_appearance():
    r1 = client.get("/?theme=1")
    r5 = client.get("/?theme=5")
    assert r1.text != r5.text


def test_invalid_theme_falls_back_to_default():
    response = client.get("/?theme=99")
    assert response.status_code == 200
    default_response = client.get("/")
    assert response.text == default_response.text


def test_theme_links_preserve_theme():
    response = client.get("/?theme=3")
    assert "?theme=3" in response.text
