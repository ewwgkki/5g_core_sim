# web/main.py
# Created by Kai Wang G on 2025-05-24.

import os
import signal
import subprocess
import sys
import threading
from collections import deque

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web.config_store import load, save

app = FastAPI(title="5G Core Sim - Web Console")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_processes = {}
_log_buffer: deque = deque(maxlen=200)  # keep last 200 lines

def _stream_output(name: str, proc: subprocess.Popen):
    for line in iter(proc.stdout.readline, b''):
        text = line.decode(errors='replace').rstrip()
        if text:
            _log_buffer.append({"service": name.upper(), "msg": text})
    proc.stdout.close()

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

SERVICE_SCRIPTS = {
    "nrf": "run_nrf.py",
    "amf": "run_amf.py",
    "udm": "run_udm.py",
}

SERVICE_HEALTH = {
    "nrf": lambda cfg: f"http://{cfg['nrf']['host']}:{cfg['nrf']['port']}/nnrf-nfm/v1/nf-instances",
    "amf": lambda cfg: f"http://{cfg['amf']['host']}:{cfg['amf']['port']}/namf-loc/v1/health",
    "udm": lambda cfg: f"http://{cfg['udm']['host']}:{cfg['udm']['port']}/nudm-uecm/v1/health",
}

# ── Page ──────────────────────────────────────────────

@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# ── Config API ────────────────────────────────────────

@app.get("/api/config")
def get_config():
    return load()

@app.post("/api/config")
def update_config(body: dict):
    current = load()
    for section, values in body.items():
        if isinstance(values, dict) and isinstance(current.get(section), dict):
            current[section].update(values)
        else:
            current[section] = values
    save(current)
    return {"ok": True, "config": current}

@app.post("/api/config/{section}")
def update_section(section: str, body: dict):
    current = load()
    if section not in current:
        raise HTTPException(status_code=404, detail=f"Unknown section: {section}")
    current[section].update(body)
    save(current)
    return {"ok": True, "config": current[section]}

# ── Service Control API ───────────────────────────────

@app.post("/api/service/{name}/start")
def start_service(name: str):
    if name not in SERVICE_SCRIPTS:
        raise HTTPException(status_code=404, detail=f"Unknown service: {name}")
    if name in _processes and _processes[name].poll() is None:
        return {"ok": False, "message": f"{name} is already running"}

    script = os.path.join(PROJECT_ROOT, SERVICE_SCRIPTS[name])
    proc = subprocess.Popen(
        [sys.executable, script],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _processes[name] = proc
    threading.Thread(target=_stream_output, args=(name, proc), daemon=True).start()
    return {"ok": True, "message": f"{name} started (pid={proc.pid})"}

@app.post("/api/service/{name}/stop")
def stop_service(name: str):
    if name not in SERVICE_SCRIPTS:
        raise HTTPException(status_code=404, detail=f"Unknown service: {name}")

    # Try stopping tracked process first
    if name in _processes and _processes[name].poll() is None:
        proc = _processes[name]
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        del _processes[name]
        return {"ok": True, "message": f"{name} stopped"}

    # Fallback: kill process occupying the service port (handles orphaned processes)
    cfg = load()
    port = cfg.get(name, {}).get("port")
    if port:
        killed = _kill_by_port(int(port))
        if killed:
            _processes.pop(name, None)
            return {"ok": True, "message": f"{name} stopped (killed process on port {port})"}

    _processes.pop(name, None)
    return {"ok": False, "message": f"{name} is not running"}


def _kill_by_port(port: int) -> bool:
    """Find and kill process listening on the given port. Returns True if killed."""
    import platform
    try:
        if platform.system() == "Darwin":
            out = subprocess.check_output(
                ["lsof", "-ti", f":{port}"], stderr=subprocess.DEVNULL
            ).decode().strip()
        else:
            out = subprocess.check_output(
                ["fuser", f"{port}/tcp"], stderr=subprocess.DEVNULL
            ).decode().strip()
        if out:
            for pid_str in out.split():
                pid = int(pid_str.strip())
                if pid != os.getpid():
                    os.kill(pid, signal.SIGTERM)
            import time
            time.sleep(1)
            return True
    except (subprocess.CalledProcessError, ValueError, ProcessLookupError):
        pass
    return False

@app.get("/api/service/{name}/status")
async def service_status(name: str):
    if name not in SERVICE_SCRIPTS:
        raise HTTPException(status_code=404, detail=f"Unknown service: {name}")

    proc_running = name in _processes and _processes[name].poll() is None
    cfg = load()
    reachable = False
    try:
        url = SERVICE_HEALTH[name](cfg)
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            reachable = resp.status_code < 500
    except Exception:
        reachable = False

    return {
        "name": name,
        "process": "running" if proc_running else "stopped",
        "reachable": reachable,
        "pid": _processes[name].pid if proc_running else None,
    }

@app.get("/api/logs")
def get_logs():
    return list(_log_buffer)

@app.get("/api/nrf/instances")
async def nrf_instances():
    cfg = load()
    url = f"http://{cfg['nrf']['host']}:{cfg['nrf']['port']}/nnrf-nfm/v1/nf-instances"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            return resp.json()
    except Exception:
        return []

@app.get("/api/services/status")
async def all_services_status():
    results = {}
    cfg = load()
    for name in SERVICE_SCRIPTS:
        proc_running = name in _processes and _processes[name].poll() is None
        reachable = False
        try:
            url = SERVICE_HEALTH[name](cfg)
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(url)
                reachable = resp.status_code < 500
        except Exception:
            reachable = False
        results[name] = {
            "process": "running" if proc_running else "stopped",
            "reachable": reachable,
            "pid": _processes[name].pid if proc_running else None,
        }
    return results
