import os
import time

import psutil
from fastapi import FastAPI, Request
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
