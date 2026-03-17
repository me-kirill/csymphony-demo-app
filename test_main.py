import os

# Use a temporary test database
os.environ["DB_PATH"] = "test_users.db"

from fastapi.testclient import TestClient

from main import app, _get_db

client = TestClient(app)


def _cleanup_db():
    db = _get_db()
    db.execute("DELETE FROM users")
    db.commit()
    db.close()


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
        assert 'href="/"' in response.text, f"Home link missing on {path}"
        assert 'href="/dashboard"' in response.text, f"Dashboard link missing on {path}"
        assert 'href="/about"' in response.text, f"About link missing on {path}"
        assert 'href="/contact"' in response.text, f"Contact link missing on {path}"


def test_nav_highlights_current_page():
    response = client.get("/about")
    assert 'href="/about" class="text-white font-semibold"' in response.text
    assert 'href="/" class="text-gray-400' in response.text


# --- Auth tests ---


def test_register_page_returns_html():
    response = client.get("/register")
    assert response.status_code == 200
    assert "Register" in response.text
    assert 'name="username"' in response.text
    assert 'name="email"' in response.text
    assert 'name="password"' in response.text


def test_login_page_returns_html():
    response = client.get("/login")
    assert response.status_code == 200
    assert "Login" in response.text
    assert 'name="username"' in response.text
    assert 'name="password"' in response.text


def test_register_creates_user():
    _cleanup_db()
    response = client.post(
        "/register",
        data={"username": "testuser", "email": "test@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/"
    assert "session" in response.cookies


def test_register_duplicate_username():
    _cleanup_db()
    client.post(
        "/register",
        data={"username": "dupuser", "email": "dup@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    response = client.post(
        "/register",
        data={"username": "dupuser", "email": "dup2@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert "already taken" in response.text


def test_register_short_username():
    response = client.post(
        "/register",
        data={"username": "ab", "email": "short@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert "at least 3 characters" in response.text


def test_register_short_password():
    response = client.post(
        "/register",
        data={"username": "validuser", "email": "valid@example.com", "password": "12345"},
    )
    assert response.status_code == 200
    assert "at least 6 characters" in response.text


def test_login_valid_credentials():
    _cleanup_db()
    client.post(
        "/register",
        data={"username": "loginuser", "email": "login@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    response = client.post(
        "/login",
        data={"username": "loginuser", "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "session" in response.cookies


def test_login_invalid_password():
    _cleanup_db()
    client.post(
        "/register",
        data={"username": "wrongpw", "email": "wrong@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    response = client.post(
        "/login",
        data={"username": "wrongpw", "password": "wrongpassword"},
    )
    assert response.status_code == 200
    assert "Invalid username or password" in response.text


def test_login_nonexistent_user():
    _cleanup_db()
    response = client.post(
        "/login",
        data={"username": "noone", "password": "whatever"},
    )
    assert response.status_code == 200
    assert "Invalid username or password" in response.text


def test_logout_clears_session():
    _cleanup_db()
    reg_response = client.post(
        "/register",
        data={"username": "logoutuser", "email": "logout@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    client.cookies.set("session", reg_response.cookies.get("session"))
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"


def test_nav_shows_login_register_when_logged_out():
    client.cookies.clear()
    response = client.get("/")
    assert 'href="/login"' in response.text
    assert 'href="/register"' in response.text


def test_nav_shows_username_when_logged_in():
    _cleanup_db()
    reg_response = client.post(
        "/register",
        data={"username": "navuser", "email": "nav@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    client.cookies.set("session", reg_response.cookies.get("session"))
    response = client.get("/")
    assert "Hello, navuser" in response.text
    assert 'href="/logout"' in response.text
    client.cookies.clear()


def test_logged_in_user_redirected_from_login():
    _cleanup_db()
    reg_response = client.post(
        "/register",
        data={"username": "rediruser", "email": "redir@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    client.cookies.set("session", reg_response.cookies.get("session"))
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302
    client.cookies.clear()


def test_logged_in_user_redirected_from_register():
    _cleanup_db()
    reg_response = client.post(
        "/register",
        data={"username": "rediruser2", "email": "redir2@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    client.cookies.set("session", reg_response.cookies.get("session"))
    response = client.get("/register", follow_redirects=False)
    assert response.status_code == 302
    client.cookies.clear()
