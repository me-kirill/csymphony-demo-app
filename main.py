import os
import sqlite3
import time
from datetime import datetime, timezone

import bcrypt
import psutil
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from itsdangerous import URLSafeSerializer

app = FastAPI()

_start_time = time.time()
_request_count = 0
_SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
_serializer = URLSafeSerializer(_SECRET_KEY)
_DB_PATH = os.environ.get("DB_PATH", "users.db")

_NAV_LINKS = [
    ("/", "Home"),
    ("/dashboard", "Dashboard"),
    ("/about", "About"),
    ("/contact", "Contact"),
]


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "username TEXT UNIQUE NOT NULL,"
        "email TEXT UNIQUE NOT NULL,"
        "password_hash TEXT NOT NULL"
        ")"
    )
    conn.commit()
    return conn


def _get_current_user(request: Request) -> dict | None:
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        data = _serializer.loads(token)
        return data
    except Exception:
        return None


def _nav_html(current_path: str, user: dict | None = None) -> str:
    links = []
    for href, label in _NAV_LINKS:
        if href == current_path:
            cls = "text-white font-semibold"
        else:
            cls = "text-gray-400 hover:text-white transition-colors"
        links.append(f'<a href="{href}" class="{cls}">{label}</a>')

    if user:
        auth_html = (
            f'<span class="text-gray-300 text-sm">Hello, {user["username"]}</span>'
            '<a href="/logout" class="text-gray-400 hover:text-white transition-colors text-sm">Logout</a>'
        )
    else:
        login_cls = "text-white font-semibold" if current_path == "/login" else "text-gray-400 hover:text-white transition-colors"
        register_cls = "text-white font-semibold" if current_path == "/register" else "text-gray-400 hover:text-white transition-colors"
        auth_html = (
            f'<a href="/login" class="{login_cls}">Login</a>'
            f'<a href="/register" class="{register_cls}">Register</a>'
        )

    return (
        '<nav class="fixed top-0 left-0 right-0 bg-gray-900/80 backdrop-blur border-b border-gray-800 z-50">'
        '<div class="max-w-4xl mx-auto px-6 py-3 flex gap-6">'
        + "".join(links)
        + '<div class="ml-auto flex gap-4 items-center">'
        + auth_html
        + "</div></div></nav>"
    )


@app.middleware("http")
async def count_requests(request: Request, call_next):
    global _request_count
    _request_count += 1
    return await call_next(request)


@app.get("/api/ping")
def ping():
    return {"pong": True}


@app.get("/api/stats")
def stats():
    process = psutil.Process(os.getpid())
    mem = process.memory_info()
    uptime_seconds = time.time() - _start_time
    hours, remainder = divmod(int(uptime_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return {
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "uptime_seconds": uptime_seconds,
        "memory_mb": round(mem.rss / 1024 / 1024, 1),
        "requests_served": _request_count,
    }


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    user = _get_current_user(request)
    nav = _nav_html("/about", user)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 min-h-screen flex items-center justify-center pt-14">
    {nav}
    <div class="bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl p-10 max-w-md text-center">
        <h1 class="text-4xl font-bold text-white mb-2">CSymphony Demo</h1>
        <p class="text-sm text-gray-500 mb-6">v0.1.0</p>
        <p class="text-gray-400 leading-relaxed">
            A lightweight demo application built with FastAPI and Tailwind CSS,
            showcasing modern web development practices with a clean, minimal interface.
        </p>
    </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    user = _get_current_user(request)
    nav = _nav_html("/", user)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-indigo-500 to-purple-600 min-h-screen flex items-center justify-center pt-14">
    {nav}
    <div class="bg-white rounded-2xl shadow-xl p-10 max-w-md text-center">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">Welcome!</h1>
        <p class="text-gray-500 mb-6">Glad to have you here.</p>
        <div class="bg-indigo-50 rounded-lg px-6 py-4">
            <p class="text-sm text-indigo-400 uppercase tracking-wide">Current Server Time</p>
            <p class="text-2xl font-semibold text-indigo-700 mt-1">{now}</p>
        </div>
    </div>
</body>
</html>"""


@app.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    user = _get_current_user(request)
    nav = _nav_html("/contact", user)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 min-h-screen flex items-center justify-center px-4 pt-14">
    {nav}
    <div class="bg-gray-800 rounded-2xl shadow-2xl p-10 max-w-lg w-full">
        <h1 class="text-3xl font-bold text-white mb-2">Contact Us</h1>
        <p class="text-gray-400 mb-8">We'd love to hear from you. Send us a message below.</p>
        <form method="POST" action="/api/contact" class="space-y-6">
            <div>
                <label for="name" class="block text-sm font-medium text-gray-300 mb-1">Name</label>
                <input type="text" id="name" name="name" required
                    class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Your name">
            </div>
            <div>
                <label for="email" class="block text-sm font-medium text-gray-300 mb-1">Email</label>
                <input type="email" id="email" name="email" required
                    class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="you@example.com">
            </div>
            <div>
                <label for="message" class="block text-sm font-medium text-gray-300 mb-1">Message</label>
                <textarea id="message" name="message" rows="4" required
                    class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    placeholder="Your message..."></textarea>
            </div>
            <button type="submit"
                class="w-full py-3 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-800">
                Send Message
            </button>
        </form>
    </div>
</body>
</html>"""


@app.post("/api/contact")
def contact_submit(name: str = Form(), email: str = Form(), message: str = Form()):
    return {"status": "ok", "name": name, "email": email, "message": message}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = _get_current_user(request)
    nav = _nav_html("/dashboard", user)
    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen flex items-center justify-center pt-14">
  {nav}
  <div class="max-w-4xl w-full px-6">
    <h1 class="text-3xl font-bold text-center mb-8">System Dashboard</h1>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="bg-gray-900 rounded-2xl p-6 shadow-lg border border-gray-800">
        <p class="text-sm text-gray-400 uppercase tracking-wide">Uptime</p>
        <p id="uptime" class="mt-2 text-2xl font-semibold text-emerald-400">--</p>
      </div>
      <div class="bg-gray-900 rounded-2xl p-6 shadow-lg border border-gray-800">
        <p class="text-sm text-gray-400 uppercase tracking-wide">Memory Usage</p>
        <p id="memory" class="mt-2 text-2xl font-semibold text-sky-400">--</p>
      </div>
      <div class="bg-gray-900 rounded-2xl p-6 shadow-lg border border-gray-800">
        <p class="text-sm text-gray-400 uppercase tracking-wide">Requests Served</p>
        <p id="requests" class="mt-2 text-2xl font-semibold text-amber-400">--</p>
      </div>
    </div>
  </div>
  <script>
    async function refresh() {{
      try {{
        const r = await fetch('/api/stats');
        const d = await r.json();
        document.getElementById('uptime').textContent = d.uptime;
        document.getElementById('memory').textContent = d.memory_mb + ' MB';
        document.getElementById('requests').textContent = d.requests_served;
      }} catch {{}}
    }}
    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>"""


def _auth_page(title: str, form_action: str, fields: str, submit_label: str,
               footer: str, error: str = "", user: dict | None = None) -> str:
    nav = _nav_html(form_action, user)
    error_html = (
        f'<div class="bg-red-900/50 border border-red-700 rounded-lg px-4 py-3 text-red-300 text-sm mb-4">{error}</div>'
        if error else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 min-h-screen flex items-center justify-center px-4 pt-14">
    {nav}
    <div class="bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl p-10 max-w-md w-full">
        <h1 class="text-3xl font-bold text-white mb-2">{title}</h1>
        {error_html}
        <form method="POST" action="{form_action}" class="space-y-6 mt-6">
            {fields}
            <button type="submit"
                class="w-full py-3 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-900">
                {submit_label}
            </button>
        </form>
        <p class="mt-6 text-center text-gray-500 text-sm">{footer}</p>
    </div>
</body>
</html>"""


def _input_field(name: str, label: str, type_: str = "text", placeholder: str = "") -> str:
    return (
        f'<div>'
        f'<label for="{name}" class="block text-sm font-medium text-gray-300 mb-1">{label}</label>'
        f'<input type="{type_}" id="{name}" name="{name}" required '
        f'class="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 '
        f'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent" '
        f'placeholder="{placeholder}">'
        f'</div>'
    )


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    user = _get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)
    fields = (
        _input_field("username", "Username", placeholder="Choose a username")
        + _input_field("email", "Email", "email", "you@example.com")
        + _input_field("password", "Password", "password", "Create a password")
    )
    return _auth_page(
        "Register", "/register", fields, "Create Account",
        'Already have an account? <a href="/login" class="text-indigo-400 hover:text-indigo-300">Login</a>',
        user=user,
    )


@app.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
):
    fields = (
        _input_field("username", "Username", placeholder="Choose a username")
        + _input_field("email", "Email", "email", "you@example.com")
        + _input_field("password", "Password", "password", "Create a password")
    )
    footer = 'Already have an account? <a href="/login" class="text-indigo-400 hover:text-indigo-300">Login</a>'

    if len(username) < 3:
        return _auth_page("Register", "/register", fields, "Create Account", footer,
                          error="Username must be at least 3 characters.")
    if len(password) < 6:
        return _auth_page("Register", "/register", fields, "Create Account", footer,
                          error="Password must be at least 6 characters.")

    db = _get_db()
    try:
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        return _auth_page("Register", "/register", fields, "Create Account", footer,
                          error="Username or email already taken.")
    db.close()

    token = _serializer.dumps({"username": username, "email": email})
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("session", token, httponly=True, samesite="lax", max_age=86400 * 7)
    return response


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = _get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)
    fields = (
        _input_field("username", "Username", placeholder="Your username")
        + _input_field("password", "Password", "password", "Your password")
    )
    return _auth_page(
        "Login", "/login", fields, "Sign In",
        'Don\'t have an account? <a href="/register" class="text-indigo-400 hover:text-indigo-300">Register</a>',
        user=user,
    )


@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(),
    password: str = Form(),
):
    fields = (
        _input_field("username", "Username", placeholder="Your username")
        + _input_field("password", "Password", "password", "Your password")
    )
    footer = 'Don\'t have an account? <a href="/register" class="text-indigo-400 hover:text-indigo-300">Register</a>'

    db = _get_db()
    row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()

    if not row or not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return _auth_page("Login", "/login", fields, "Sign In", footer,
                          error="Invalid username or password.")

    token = _serializer.dumps({"username": row["username"], "email": row["email"]})
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("session", token, httponly=True, samesite="lax", max_age=86400 * 7)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session")
    return response
