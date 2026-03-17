import os
import time
from datetime import datetime, timezone

import psutil
from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

_start_time = time.time()
_request_count = 0

_NAV_LINKS = [
    ("/", "Home"),
    ("/dashboard", "Dashboard"),
    ("/about", "About"),
    ("/contact", "Contact"),
]


def _nav_html(current_path: str) -> str:
    links = []
    for href, label in _NAV_LINKS:
        if href == current_path:
            cls = "text-white font-semibold"
        else:
            cls = "text-gray-400 hover:text-white transition-colors"
        links.append(f'<a href="{href}" class="{cls}">{label}</a>')
    return (
        '<nav class="fixed top-0 left-0 right-0 bg-gray-900/80 backdrop-blur border-b border-gray-800 z-50">'
        '<div class="max-w-4xl mx-auto px-6 py-3 flex gap-6">'
        + "".join(links)
        + "</div></nav>"
    )


# ── Theme definitions ──────────────────────────────────────────────────────
# Each theme provides unique fonts, colors, shapes, and effects via CSS variables.
# The default theme (theme=0 or absent) uses the original Tailwind-based HTML.

THEMES = _THEMES = {
    1: {
        "name": "Cyberpunk",
        "color": "#00fff5",
        "font_url": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&display=swap",
        "css": """
:root {
    --font: 'JetBrains Mono', monospace;
    --font-heading: 'JetBrains Mono', monospace;
    --bg-page: #08080f;
    --bg-nav: rgba(8,8,15,0.95);
    --nav-border: rgba(0,255,245,0.2);
    --bg-card: #0e0e1a;
    --card-border: rgba(0,255,245,0.15);
    --card-shadow: 0 0 40px rgba(0,255,245,0.05);
    --card-radius: 2px;
    --text-heading: #00fff5;
    --text-body: #8888aa;
    --text-muted: #555577;
    --text-nav: #555577;
    --text-nav-active: #00fff5;
    --accent: #ff00aa;
    --accent-hover: #ff33bb;
    --accent-text: #fff;
    --bg-input: #0a0a16;
    --input-border: rgba(0,255,245,0.1);
    --input-focus: #00fff5;
    --input-focus-ring: rgba(0,255,245,0.12);
    --input-text: #ccccee;
    --stat-1: #00fff5;
    --stat-2: #ff00aa;
    --stat-3: #faff00;
    --heading-transform: uppercase;
    --heading-tracking: 0.08em;
    --time-bg: rgba(0,255,245,0.04);
    --time-label: #00fff5;
    --time-value: #ff00aa;
}
body::before {
    content: ''; position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 20% 40%, rgba(0,255,245,0.04) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 60%, rgba(255,0,170,0.03) 0%, transparent 60%);
    pointer-events: none; z-index: 0;
}
h1 { text-shadow: 0 0 40px rgba(0,255,245,0.25); }
.card::after {
    content: ''; position: absolute; inset: -1px;
    background: linear-gradient(135deg, rgba(0,255,245,0.15), transparent 40%, rgba(255,0,170,0.15));
    border-radius: var(--card-radius); z-index: -1; pointer-events: none;
}
.stat-card::after {
    content: ''; position: absolute; inset: -1px;
    background: linear-gradient(180deg, rgba(0,255,245,0.1), transparent);
    border-radius: var(--card-radius); z-index: -1; pointer-events: none;
}
""",
    },
    2: {
        "name": "Earth",
        "color": "#c2703e",
        "font_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap",
        "css": """
:root {
    --font: 'Source Sans 3', sans-serif;
    --font-heading: 'Playfair Display', serif;
    --bg-page: #faf6f0;
    --bg-nav: rgba(250,246,240,0.92);
    --nav-border: #e0d5c5;
    --bg-card: #ffffff;
    --card-border: #ebe3d6;
    --card-shadow: 0 2px 16px rgba(60,40,20,0.06);
    --card-radius: 16px;
    --text-heading: #3d2b1f;
    --text-body: #5c4a3a;
    --text-muted: #9a8a7a;
    --text-nav: #9a8a7a;
    --text-nav-active: #3d2b1f;
    --accent: #c2703e;
    --accent-hover: #a85c30;
    --accent-text: #fff;
    --bg-input: #faf6f0;
    --input-border: #d5c9b8;
    --input-focus: #c2703e;
    --input-focus-ring: rgba(194,112,62,0.12);
    --input-text: #3d2b1f;
    --stat-1: #5a8f6a;
    --stat-2: #2e7d9e;
    --stat-3: #c2703e;
    --heading-transform: none;
    --heading-tracking: -0.01em;
    --time-bg: #f5ede3;
    --time-label: #c2703e;
    --time-value: #3d2b1f;
}
""",
    },
    3: {
        "name": "Ocean",
        "color": "#0891b2",
        "font_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;800&display=swap",
        "css": """
:root {
    --font: 'Plus Jakarta Sans', sans-serif;
    --font-heading: 'Plus Jakarta Sans', sans-serif;
    --bg-page: #f0f9ff;
    --bg-nav: rgba(255,255,255,0.6);
    --nav-border: rgba(186,230,253,0.6);
    --bg-card: rgba(255,255,255,0.55);
    --card-border: rgba(186,230,253,0.4);
    --card-shadow: 0 8px 32px rgba(0,100,160,0.06);
    --card-radius: 20px;
    --text-heading: #0c4a6e;
    --text-body: #334155;
    --text-muted: #64748b;
    --text-nav: #64748b;
    --text-nav-active: #0c4a6e;
    --accent: #0891b2;
    --accent-hover: #0e7490;
    --accent-text: #fff;
    --bg-input: rgba(255,255,255,0.6);
    --input-border: rgba(186,230,253,0.6);
    --input-focus: #0891b2;
    --input-focus-ring: rgba(8,145,178,0.12);
    --input-text: #0c4a6e;
    --stat-1: #0891b2;
    --stat-2: #0ea5e9;
    --stat-3: #06b6d4;
    --heading-transform: none;
    --heading-tracking: -0.02em;
    --time-bg: rgba(8,145,178,0.06);
    --time-label: #0891b2;
    --time-value: #0c4a6e;
}
body { background: linear-gradient(160deg, #dbeafe 0%, #f0f9ff 30%, #ecfeff 70%, #cffafe 100%) !important; }
.card, .stat-card { backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
nav { backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); }
""",
    },
    4: {
        "name": "Sunset",
        "color": "#ff6b35",
        "font_url": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap",
        "css": """
:root {
    --font: 'Space Grotesk', sans-serif;
    --font-heading: 'Space Grotesk', sans-serif;
    --bg-page: #150a28;
    --bg-nav: rgba(21,10,40,0.9);
    --nav-border: rgba(255,107,53,0.15);
    --bg-card: rgba(25,12,45,0.7);
    --card-border: rgba(255,107,53,0.12);
    --card-shadow: 0 8px 40px rgba(255,107,53,0.06);
    --card-radius: 16px;
    --text-heading: #ffe0c8;
    --text-body: #b890c8;
    --text-muted: #705880;
    --text-nav: #705880;
    --text-nav-active: #ffe0c8;
    --accent: #ff6b35;
    --accent-hover: #ff8555;
    --accent-text: #fff;
    --bg-input: rgba(30,15,55,0.7);
    --input-border: rgba(255,107,53,0.15);
    --input-focus: #ff6b35;
    --input-focus-ring: rgba(255,107,53,0.12);
    --input-text: #ffe0c8;
    --stat-1: #ff6b35;
    --stat-2: #f72585;
    --stat-3: #ffd166;
    --heading-transform: none;
    --heading-tracking: -0.01em;
    --time-bg: rgba(255,107,53,0.06);
    --time-label: #ff6b35;
    --time-value: #ffd166;
}
body::before {
    content: ''; position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 25% 15%, rgba(255,107,53,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 75% 85%, rgba(247,37,133,0.05) 0%, transparent 55%);
    pointer-events: none; z-index: 0;
}
.card, .stat-card { backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); }
nav { backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
""",
    },
    5: {
        "name": "Nordic",
        "color": "#171717",
        "font_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        "css": """
:root {
    --font: 'Inter', -apple-system, sans-serif;
    --font-heading: 'Inter', -apple-system, sans-serif;
    --bg-page: #ffffff;
    --bg-nav: rgba(255,255,255,0.92);
    --nav-border: #e5e5e5;
    --bg-card: #ffffff;
    --card-border: #e5e5e5;
    --card-shadow: none;
    --card-radius: 8px;
    --text-heading: #0a0a0a;
    --text-body: #404040;
    --text-muted: #a3a3a3;
    --text-nav: #a3a3a3;
    --text-nav-active: #0a0a0a;
    --accent: #0a0a0a;
    --accent-hover: #262626;
    --accent-text: #fff;
    --bg-input: #fafafa;
    --input-border: #e5e5e5;
    --input-focus: #0a0a0a;
    --input-focus-ring: rgba(10,10,10,0.08);
    --input-text: #0a0a0a;
    --stat-1: #0a0a0a;
    --stat-2: #525252;
    --stat-3: #737373;
    --heading-transform: none;
    --heading-tracking: -0.03em;
    --time-bg: #fafafa;
    --time-label: #a3a3a3;
    --time-value: #0a0a0a;
}
nav { backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
""",
    },
}

_BASE_CSS = (
    "*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}"
    "body{font-family:var(--font);background:var(--bg-page);color:var(--text-body);min-height:100vh}"
    "h1,h2,h3{font-family:var(--font-heading);color:var(--text-heading);"
    "text-transform:var(--heading-transform,none);letter-spacing:var(--heading-tracking,normal)}"
    "@keyframes fadeIn{from{opacity:0}to{opacity:1}}body{animation:fadeIn .3s ease}"
    "nav{position:fixed;top:0;left:0;right:0;background:var(--bg-nav);"
    "border-bottom:1px solid var(--nav-border);z-index:50}"
    ".nav-inner{max-width:56rem;margin:0 auto;padding:.75rem 1.5rem;display:flex;gap:1.5rem}"
    ".nav-link,.nav-link-active{text-decoration:none;font-size:.875rem;transition:color .2s}"
    ".nav-link{color:var(--text-nav)}.nav-link:hover{color:var(--text-nav-active)}"
    ".nav-link-active{color:var(--text-nav-active);font-weight:600}"
    "main{min-height:100vh;display:flex;align-items:center;justify-content:center;"
    "padding:5rem 1rem 6rem;position:relative;z-index:1}"
    ".card{background:var(--bg-card);border:1px solid var(--card-border);"
    "border-radius:var(--card-radius,16px);box-shadow:var(--card-shadow,none);"
    "padding:2.5rem;max-width:28rem;width:100%;position:relative}"
    ".card-wide{max-width:56rem}.text-center{text-align:center}"
    "h1{font-size:2.25rem;font-weight:700;line-height:1.2}"
    ".subtitle{color:var(--text-muted);margin:.75rem 0 1.5rem;font-size:1.05rem}"
    ".time-box{background:var(--time-bg);border-radius:8px;padding:1rem 1.5rem;margin-top:.5rem}"
    ".time-label{font-size:.75rem;color:var(--time-label);text-transform:uppercase;"
    "letter-spacing:.05em}"
    ".time-value{font-size:1.5rem;font-weight:600;color:var(--time-value);margin-top:.25rem}"
    ".stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:2rem}"
    "@media(max-width:640px){.stats-grid{grid-template-columns:1fr}}"
    ".stat-card{background:var(--bg-card);border:1px solid var(--card-border);"
    "border-radius:var(--card-radius,16px);box-shadow:var(--card-shadow,none);"
    "padding:1.5rem;position:relative}"
    ".stat-label{font-size:.75rem;color:var(--text-muted);text-transform:uppercase;"
    "letter-spacing:.05em}"
    ".stat-value{font-size:1.5rem;font-weight:600;margin-top:.5rem}"
    ".stat-1{color:var(--stat-1)}.stat-2{color:var(--stat-2)}.stat-3{color:var(--stat-3)}"
    ".form-group{margin-bottom:1.25rem}"
    ".form-label{display:block;font-size:.875rem;font-weight:500;"
    "color:var(--text-body);margin-bottom:.375rem}"
    ".form-input{width:100%;padding:.75rem 1rem;background:var(--bg-input);"
    "border:1px solid var(--input-border);border-radius:8px;color:var(--input-text);"
    "font-family:var(--font);font-size:1rem;transition:border-color .2s,box-shadow .2s;outline:none}"
    ".form-input:focus{border-color:var(--input-focus);"
    "box-shadow:0 0 0 3px var(--input-focus-ring)}"
    ".form-input::placeholder{color:var(--text-muted)}"
    "textarea.form-input{resize:none;min-height:6rem}"
    ".btn{display:block;width:100%;padding:.75rem 1.5rem;margin-top:1.5rem;"
    "background:var(--accent);color:var(--accent-text);border:none;border-radius:8px;"
    "font-family:var(--font);font-weight:600;font-size:1rem;cursor:pointer;transition:background .2s}"
    ".btn:hover{background:var(--accent-hover)}"
    ".version{font-size:.875rem;color:var(--text-muted);margin:.25rem 0 1.5rem}"
    ".description{color:var(--text-body);line-height:1.7}"
)

_DASHBOARD_SCRIPTS = (
    "<script>"
    "async function refresh(){"
    "try{"
    "const r=await fetch('/api/stats');"
    "const d=await r.json();"
    "document.getElementById('uptime').textContent=d.uptime;"
    "document.getElementById('memory').textContent=d.memory_mb+' MB';"
    "document.getElementById('requests').textContent=d.requests_served;"
    "}catch(e){}}"
    "refresh();setInterval(refresh,5000);"
    "</script>"
)


def _switcher_html(current_theme: int, current_path: str) -> str:
    """Floating theme picker bar with inline styles (works in any context)."""
    options = [
        (0, "Default", "#6366f1"),
        (1, "Cyberpunk", "#00fff5"),
        (2, "Earth", "#c2703e"),
        (3, "Ocean", "#0891b2"),
        (4, "Sunset", "#ff6b35"),
        (5, "Nordic", "#171717"),
    ]
    items = []
    for tid, name, color in options:
        href = current_path if tid == 0 else f"{current_path}?theme={tid}"
        active = tid == current_theme
        bg = "rgba(255,255,255,0.15)" if active else "transparent"
        txt = "#fff" if active else "rgba(255,255,255,0.5)"
        items.append(
            f'<a href="{href}" style="display:flex;align-items:center;gap:6px;'
            f"padding:6px 12px;border-radius:999px;text-decoration:none;"
            f"color:{txt};font-size:12px;background:{bg};"
            f'transition:all .2s;white-space:nowrap;font-family:system-ui,sans-serif">'
            f'<span style="width:8px;height:8px;border-radius:50%;'
            f'background:{color};flex-shrink:0"></span>{name}</a>'
        )
    return (
        '<div style="position:fixed;bottom:24px;left:50%;transform:translateX(-50%);'
        "display:flex;align-items:center;gap:2px;background:rgba(0,0,0,0.85);"
        "backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);"
        "padding:4px;border-radius:999px;z-index:100;"
        'border:1px solid rgba(255,255,255,0.08);box-shadow:0 4px 24px rgba(0,0,0,0.3)">'
        '<span style="color:rgba(255,255,255,0.35);font-size:10px;font-family:system-ui,sans-serif;'
        'text-transform:uppercase;letter-spacing:0.05em;padding:0 8px">Theme</span>'
        + "".join(items)
        + "</div>"
    )


def _themed_nav(current_path: str, theme_id: int) -> str:
    """Navigation bar for themed pages (CSS-variable based)."""
    links = []
    suffix = f"?theme={theme_id}"
    for href, label in _NAV_LINKS:
        cls = "nav-link-active" if href == current_path else "nav-link"
        links.append(f'<a href="{href}{suffix}" class="{cls}">{label}</a>')
    return "<nav><div class='nav-inner'>" + "".join(links) + "</div></nav>"


def _themed_page(
    title: str,
    theme_id: int,
    current_path: str,
    content: str,
    extra_scripts: str = "",
) -> str:
    """Full HTML page shell for themed pages (1-5)."""
    theme = _THEMES[theme_id]
    nav = _themed_nav(current_path, theme_id)
    switcher = _switcher_html(theme_id, current_path)
    return (
        "<!DOCTYPE html>"
        '<html lang="en"><head>'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f"<title>{title}</title>"
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link href="{theme["font_url"]}" rel="stylesheet">'
        f"<style>{_BASE_CSS}\n{theme['css']}</style>"
        f"</head><body>{nav}{content}{switcher}{extra_scripts}</body></html>"
    )


# ── Middleware ─────────────────────────────────────────────────────────────


@app.middleware("http")
async def count_requests(request: Request, call_next):
    global _request_count
    _request_count += 1
    return await call_next(request)


# ── API routes ─────────────────────────────────────────────────────────────


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


@app.post("/api/contact")
def contact_submit(name: str = Form(), email: str = Form(), message: str = Form()):
    return {"status": "ok", "name": name, "email": email, "message": message}


# ── HTML routes ────────────────────────────────────────────────────────────


@app.get("/about", response_class=HTMLResponse)
def about(theme: int = Query(default=0)):
    if theme in _THEMES:
        content = (
            '<main><div class="card text-center">'
            "<h1>CSymphony Demo</h1>"
            '<p class="version">v0.1.0</p>'
            '<p class="description">'
            "A lightweight demo application built with FastAPI and Tailwind CSS, "
            "showcasing modern web development practices with a clean, minimal interface."
            "</p></div></main>"
        )
        return _themed_page("About", theme, "/about", content)
    nav = _nav_html("/about")
    switcher = _switcher_html(0, "/about")
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
    {switcher}
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def landing(theme: int = Query(default=0)):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if theme in _THEMES:
        content = (
            '<main><div class="card text-center">'
            "<h1>Welcome!</h1>"
            '<p class="subtitle">Glad to have you here.</p>'
            '<div class="time-box">'
            '<p class="time-label">Current Server Time</p>'
            f'<p class="time-value">{now}</p>'
            "</div></div></main>"
        )
        return _themed_page("Welcome", theme, "/", content)
    nav = _nav_html("/")
    switcher = _switcher_html(0, "/")
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
    {switcher}
</body>
</html>"""


@app.get("/contact", response_class=HTMLResponse)
def contact_page(theme: int = Query(default=0)):
    if theme in _THEMES:
        content = (
            '<main><div class="card">'
            "<h1>Contact Us</h1>"
            "<p class=\"subtitle\">We'd love to hear from you."
            " Send us a message below.</p>"
            '<form method="POST" action="/api/contact">'
            '<div class="form-group">'
            '<label for="name" class="form-label">Name</label>'
            '<input type="text" id="name" name="name" required'
            ' class="form-input" placeholder="Your name">'
            "</div>"
            '<div class="form-group">'
            '<label for="email" class="form-label">Email</label>'
            '<input type="email" id="email" name="email" required'
            ' class="form-input" placeholder="you@example.com">'
            "</div>"
            '<div class="form-group">'
            '<label for="message" class="form-label">Message</label>'
            '<textarea id="message" name="message" rows="4" required'
            ' class="form-input" placeholder="Your message..."></textarea>'
            "</div>"
            '<button type="submit" class="btn">Send Message</button>'
            "</form></div></main>"
        )
        return _themed_page("Contact Us", theme, "/contact", content)
    nav = _nav_html("/contact")
    switcher = _switcher_html(0, "/contact")
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
    {switcher}
</body>
</html>"""


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(theme: int = Query(default=0)):
    if theme in _THEMES:
        content = (
            '<main><div class="card card-wide text-center">'
            "<h1>System Dashboard</h1>"
            '<div class="stats-grid">'
            '<div class="stat-card">'
            '<p class="stat-label">Uptime</p>'
            '<p class="stat-value stat-1" id="uptime">--</p>'
            "</div>"
            '<div class="stat-card">'
            '<p class="stat-label">Memory Usage</p>'
            '<p class="stat-value stat-2" id="memory">--</p>'
            "</div>"
            '<div class="stat-card">'
            '<p class="stat-label">Requests Served</p>'
            '<p class="stat-value stat-3" id="requests">--</p>'
            "</div>"
            "</div></div></main>"
        )
        return _themed_page(
            "Dashboard", theme, "/dashboard", content, _DASHBOARD_SCRIPTS
        )
    nav = _nav_html("/dashboard")
    switcher = _switcher_html(0, "/dashboard")
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
  {switcher}
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
