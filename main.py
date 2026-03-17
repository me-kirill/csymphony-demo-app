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

THEMES = {
    1: {
        "name": "Midnight",
        "body_bg": "bg-gray-950",
        "landing_bg": "bg-gradient-to-br from-indigo-600 to-purple-700",
        "nav_bg": "bg-gray-900/80 backdrop-blur border-b border-gray-800",
        "nav_link": "text-gray-400 hover:text-white",
        "nav_active": "text-white font-semibold",
        "card_bg": "bg-gray-900 border border-gray-800",
        "landing_card_bg": "bg-white",
        "heading": "text-white",
        "landing_heading": "text-gray-800",
        "text": "text-gray-400",
        "landing_text": "text-gray-500",
        "accent": "indigo",
        "stat_colors": ["text-emerald-400", "text-sky-400", "text-amber-400"],
        "input_bg": "bg-gray-700 border-gray-600 text-white placeholder-gray-400",
        "btn": "bg-indigo-600 hover:bg-indigo-700 text-white",
        "badge_bg": "bg-indigo-50",
        "badge_text": "text-indigo-400",
        "badge_value": "text-indigo-700",
        "switcher_bg": "bg-gray-800 border-gray-700",
        "switcher_text": "text-gray-300",
    },
    2: {
        "name": "Ocean",
        "body_bg": "bg-slate-900",
        "landing_bg": "bg-gradient-to-br from-cyan-500 to-blue-700",
        "nav_bg": "bg-slate-800/90 backdrop-blur border-b border-slate-700",
        "nav_link": "text-slate-400 hover:text-cyan-300",
        "nav_active": "text-cyan-300 font-semibold",
        "card_bg": "bg-slate-800 border border-slate-700",
        "landing_card_bg": "bg-white/95 backdrop-blur",
        "heading": "text-cyan-100",
        "landing_heading": "text-slate-800",
        "text": "text-slate-400",
        "landing_text": "text-slate-500",
        "accent": "cyan",
        "stat_colors": ["text-cyan-400", "text-teal-400", "text-blue-400"],
        "input_bg": "bg-slate-700 border-slate-600 text-white placeholder-slate-400",
        "btn": "bg-cyan-600 hover:bg-cyan-700 text-white",
        "badge_bg": "bg-cyan-50",
        "badge_text": "text-cyan-500",
        "badge_value": "text-cyan-700",
        "switcher_bg": "bg-slate-800 border-slate-600",
        "switcher_text": "text-slate-300",
    },
    3: {
        "name": "Sunset",
        "body_bg": "bg-stone-950",
        "landing_bg": "bg-gradient-to-br from-orange-400 via-rose-500 to-pink-600",
        "nav_bg": "bg-stone-900/90 backdrop-blur border-b border-stone-800",
        "nav_link": "text-stone-400 hover:text-orange-300",
        "nav_active": "text-orange-300 font-semibold",
        "card_bg": "bg-stone-900 border border-stone-800",
        "landing_card_bg": "bg-white/95 backdrop-blur",
        "heading": "text-orange-100",
        "landing_heading": "text-stone-800",
        "text": "text-stone-400",
        "landing_text": "text-stone-500",
        "accent": "orange",
        "stat_colors": ["text-orange-400", "text-rose-400", "text-amber-400"],
        "input_bg": "bg-stone-700 border-stone-600 text-white placeholder-stone-400",
        "btn": "bg-orange-500 hover:bg-orange-600 text-white",
        "badge_bg": "bg-orange-50",
        "badge_text": "text-orange-500",
        "badge_value": "text-orange-700",
        "switcher_bg": "bg-stone-800 border-stone-700",
        "switcher_text": "text-stone-300",
    },
    4: {
        "name": "Forest",
        "body_bg": "bg-neutral-950",
        "landing_bg": "bg-gradient-to-br from-emerald-500 to-teal-700",
        "nav_bg": "bg-neutral-900/90 backdrop-blur border-b border-neutral-800",
        "nav_link": "text-neutral-400 hover:text-emerald-300",
        "nav_active": "text-emerald-300 font-semibold",
        "card_bg": "bg-neutral-900 border border-neutral-800",
        "landing_card_bg": "bg-white/95 backdrop-blur",
        "heading": "text-emerald-100",
        "landing_heading": "text-neutral-800",
        "text": "text-neutral-400",
        "landing_text": "text-neutral-500",
        "accent": "emerald",
        "stat_colors": ["text-emerald-400", "text-lime-400", "text-teal-400"],
        "input_bg": "bg-neutral-700 border-neutral-600 text-white placeholder-neutral-400",
        "btn": "bg-emerald-600 hover:bg-emerald-700 text-white",
        "badge_bg": "bg-emerald-50",
        "badge_text": "text-emerald-500",
        "badge_value": "text-emerald-700",
        "switcher_bg": "bg-neutral-800 border-neutral-700",
        "switcher_text": "text-neutral-300",
    },
    5: {
        "name": "Minimal",
        "body_bg": "bg-gray-50",
        "landing_bg": "bg-white",
        "nav_bg": "bg-white/90 backdrop-blur border-b border-gray-200",
        "nav_link": "text-gray-500 hover:text-gray-900",
        "nav_active": "text-gray-900 font-semibold",
        "card_bg": "bg-white border border-gray-200 shadow-sm",
        "landing_card_bg": "bg-white border border-gray-200 shadow-lg",
        "heading": "text-gray-900",
        "landing_heading": "text-gray-900",
        "text": "text-gray-500",
        "landing_text": "text-gray-500",
        "accent": "gray",
        "stat_colors": ["text-gray-900", "text-gray-900", "text-gray-900"],
        "input_bg": "bg-gray-100 border-gray-300 text-gray-900 placeholder-gray-400",
        "btn": "bg-gray-900 hover:bg-gray-800 text-white",
        "badge_bg": "bg-gray-100",
        "badge_text": "text-gray-500",
        "badge_value": "text-gray-900",
        "switcher_bg": "bg-white border-gray-200 shadow-sm",
        "switcher_text": "text-gray-600",
    },
}

DEFAULT_THEME = 1


def _get_theme(theme_id: int | None) -> dict:
    if theme_id is None or theme_id not in THEMES:
        return THEMES[DEFAULT_THEME]
    return THEMES[theme_id]


def _theme_switcher_html(current_theme: int, current_path: str) -> str:
    t = _get_theme(current_theme)
    buttons = []
    colors = {
        1: "bg-indigo-500",
        2: "bg-cyan-500",
        3: "bg-orange-500",
        4: "bg-emerald-500",
        5: "bg-gray-900",
    }
    for tid, theme in THEMES.items():
        active = "ring-2 ring-offset-2 ring-offset-gray-900 scale-110" if tid == current_theme else "opacity-60 hover:opacity-100"
        buttons.append(
            f'<a href="{current_path}?theme={tid}" '
            f'class="{colors[tid]} w-7 h-7 rounded-full inline-block transition-all {active}" '
            f'title="{theme["name"]}"></a>'
        )
    return (
        f'<div class="fixed bottom-6 right-6 {t["switcher_bg"]} border rounded-2xl px-4 py-3 z-50 flex items-center gap-3 shadow-lg">'
        f'<span class="{t["switcher_text"]} text-xs font-medium uppercase tracking-wide mr-1">Theme</span>'
        + "".join(buttons)
        + "</div>"
    )


def _nav_html(current_path: str, theme_id: int) -> str:
    t = _get_theme(theme_id)
    links = []
    for href, label in _NAV_LINKS:
        if href == current_path:
            cls = t["nav_active"]
        else:
            cls = t["nav_link"] + " transition-colors"
        links.append(f'<a href="{href}?theme={theme_id}" class="{cls}">{label}</a>')
    return (
        f'<nav class="fixed top-0 left-0 right-0 {t["nav_bg"]} z-50">'
        f'<div class="max-w-4xl mx-auto px-6 py-3 flex gap-6">'
        + "".join(links)
        + "</div></nav>"
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
def about(theme: int | None = Query(default=None)):
    tid = theme if theme in THEMES else DEFAULT_THEME
    t = _get_theme(tid)
    nav = _nav_html("/about", tid)
    switcher = _theme_switcher_html(tid, "/about")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="{t['body_bg']} min-h-screen flex items-center justify-center pt-14">
    {nav}
    <div class="{t['card_bg']} rounded-2xl shadow-2xl p-10 max-w-md text-center">
        <h1 class="text-4xl font-bold {t['heading']} mb-2">CSymphony Demo</h1>
        <p class="text-sm {t['text']} mb-6">v0.1.0</p>
        <p class="{t['text']} leading-relaxed">
            A lightweight demo application built with FastAPI and Tailwind CSS,
            showcasing modern web development practices with a clean, minimal interface.
        </p>
    </div>
    {switcher}
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def landing(theme: int | None = Query(default=None)):
    tid = theme if theme in THEMES else DEFAULT_THEME
    t = _get_theme(tid)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    nav = _nav_html("/", tid)
    switcher = _theme_switcher_html(tid, "/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="{t['landing_bg']} min-h-screen flex items-center justify-center pt-14">
    {nav}
    <div class="{t['landing_card_bg']} rounded-2xl shadow-xl p-10 max-w-md text-center">
        <h1 class="text-4xl font-bold {t['landing_heading']} mb-4">Welcome!</h1>
        <p class="{t['landing_text']} mb-6">Glad to have you here.</p>
        <div class="{t['badge_bg']} rounded-lg px-6 py-4">
            <p class="text-sm {t['badge_text']} uppercase tracking-wide">Current Server Time</p>
            <p class="text-2xl font-semibold {t['badge_value']} mt-1">{now}</p>
        </div>
    </div>
    {switcher}
</body>
</html>"""


@app.get("/contact", response_class=HTMLResponse)
def contact_page(theme: int | None = Query(default=None)):
    tid = theme if theme in THEMES else DEFAULT_THEME
    t = _get_theme(tid)
    nav = _nav_html("/contact", tid)
    switcher = _theme_switcher_html(tid, "/contact")
    accent = t["accent"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="{t['body_bg']} min-h-screen flex items-center justify-center px-4 pt-14">
    {nav}
    <div class="{t['card_bg']} rounded-2xl shadow-2xl p-10 max-w-lg w-full">
        <h1 class="text-3xl font-bold {t['heading']} mb-2">Contact Us</h1>
        <p class="{t['text']} mb-8">We'd love to hear from you. Send us a message below.</p>
        <form method="POST" action="/api/contact" class="space-y-6">
            <div>
                <label for="name" class="block text-sm font-medium {t['text']} mb-1">Name</label>
                <input type="text" id="name" name="name" required
                    class="w-full px-4 py-3 {t['input_bg']} rounded-lg focus:outline-none focus:ring-2 focus:ring-{accent}-500 focus:border-transparent"
                    placeholder="Your name">
            </div>
            <div>
                <label for="email" class="block text-sm font-medium {t['text']} mb-1">Email</label>
                <input type="email" id="email" name="email" required
                    class="w-full px-4 py-3 {t['input_bg']} rounded-lg focus:outline-none focus:ring-2 focus:ring-{accent}-500 focus:border-transparent"
                    placeholder="you@example.com">
            </div>
            <div>
                <label for="message" class="block text-sm font-medium {t['text']} mb-1">Message</label>
                <textarea id="message" name="message" rows="4" required
                    class="w-full px-4 py-3 {t['input_bg']} rounded-lg focus:outline-none focus:ring-2 focus:ring-{accent}-500 focus:border-transparent resize-none"
                    placeholder="Your message..."></textarea>
            </div>
            <button type="submit"
                class="w-full py-3 px-6 {t['btn']} font-semibold rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-{accent}-500 focus:ring-offset-2">
                Send Message
            </button>
        </form>
    </div>
    {switcher}
</body>
</html>"""


@app.post("/api/contact")
def contact_submit(name: str = Form(), email: str = Form(), message: str = Form()):
    return {"status": "ok", "name": name, "email": email, "message": message}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(theme: int | None = Query(default=None)):
    tid = theme if theme in THEMES else DEFAULT_THEME
    t = _get_theme(tid)
    nav = _nav_html("/dashboard", tid)
    switcher = _theme_switcher_html(tid, "/dashboard")
    sc = t["stat_colors"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="{t['body_bg']} min-h-screen flex items-center justify-center pt-14">
  {nav}
  <div class="max-w-4xl w-full px-6">
    <h1 class="text-3xl font-bold text-center mb-8 {t['heading']}">System Dashboard</h1>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="{t['card_bg']} rounded-2xl p-6 shadow-lg">
        <p class="text-sm {t['text']} uppercase tracking-wide">Uptime</p>
        <p id="uptime" class="mt-2 text-2xl font-semibold {sc[0]}">--</p>
      </div>
      <div class="{t['card_bg']} rounded-2xl p-6 shadow-lg">
        <p class="text-sm {t['text']} uppercase tracking-wide">Memory Usage</p>
        <p id="memory" class="mt-2 text-2xl font-semibold {sc[1]}">--</p>
      </div>
      <div class="{t['card_bg']} rounded-2xl p-6 shadow-lg">
        <p class="text-sm {t['text']} uppercase tracking-wide">Requests Served</p>
        <p id="requests" class="mt-2 text-2xl font-semibold {sc[2]}">--</p>
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
