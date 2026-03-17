import os
import time
from datetime import datetime, timezone

import psutil
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

_start_time = time.time()
_request_count = 0


@app.middleware("http")
async def count_requests(request: Request, call_next):
    global _request_count
    _request_count += 1
    return await call_next(request)


@app.get("/api/ping")
def ping():
    return {"pong": True}


@app.get("/about", response_class=HTMLResponse)
def about():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 min-h-screen flex items-center justify-center">
    <div class="bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl p-10 max-w-md text-center">
        <h1 class="text-4xl font-bold text-white mb-2">CSymphony Demo</h1>
        <p class="text-sm text-gray-500 mb-6">v0.1.0</p>
        <p class="text-gray-400 leading-relaxed">
            A lightweight demo application built with FastAPI and Tailwind CSS,
            showcasing modern web development practices with a clean, minimal interface.
        </p>
        <div class="mt-8">
            <a href="/" class="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">&larr; Back to Home</a>
        </div>
    </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def landing():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-indigo-500 to-purple-600 min-h-screen flex items-center justify-center">
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
def contact_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 min-h-screen flex items-center justify-center px-4">
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


_DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen flex items-center justify-center">
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
    async function refresh() {
      try {
        const r = await fetch('/api/stats');
        const d = await r.json();
        document.getElementById('uptime').textContent = d.uptime;
        document.getElementById('memory').textContent = d.memory_mb + ' MB';
        document.getElementById('requests').textContent = d.requests_served;
      } catch {}
    }
    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>
"""


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return _DASHBOARD_HTML
