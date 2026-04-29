"""
NEXUS — Unified Launcher
=========================
Starts both servers simultaneously:
  - FastAPI  backend  → http://localhost:8000  (REST API + /docs)
  - Streamlit frontend → http://localhost:8501  (Dashboard UI)

Usage:
    python start.py
"""

import subprocess
import sys
import time
import signal
import os

API_PORT  = 8000
DASH_PORT = 8501
ROOT      = os.path.dirname(os.path.abspath(__file__))

BANNER = r"""
  _   _ _______  ____  _   _ ____
 | \ | | ____\ \/ /  \/  |/ ___|
 |  \| |  _|  \  /| |\/| |\___ \
 | |\  | |___ /  \| |  | | ___) |
 |_| \_|_____/_/\_\_|  |_||____/

  Retail Intelligence Platform  v2.0
  API  --> http://localhost:{api}
  Dash --> http://localhost:{dash}
  API Docs --> http://localhost:{api}/docs
""".format(api=API_PORT, dash=DASH_PORT)


def launch():
    print(BANNER)

    procs = []

    # ── FastAPI server ─────────────────────────────────────────────────────
    api_cmd = [
        sys.executable, "-m", "uvicorn",
        "server:app",
        "--host", "0.0.0.0",
        "--port", str(API_PORT),
        "--reload",
        "--log-level", "info",
    ]
    print(f"[NEXUS] Starting API server on port {API_PORT}...")
    api_proc = subprocess.Popen(
        api_cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    procs.append(("API", api_proc))
    time.sleep(2)  # Give the API a head-start before Streamlit boots

    # ── Streamlit dashboard ────────────────────────────────────────────────
    dash_cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(ROOT, "app.py"),
        "--server.port", str(DASH_PORT),
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
    ]
    print(f"[NEXUS] Starting dashboard on port {DASH_PORT}...")
    dash_proc = subprocess.Popen(
        dash_cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    procs.append(("DASH", dash_proc))

    print("[NEXUS] Both services are running. Press Ctrl+C to stop all.\n")

    # ── Stream combined logs ───────────────────────────────────────────────
    import threading

    def stream(name, proc):
        for line in proc.stdout:
            print(f"[{name}] {line}", end="")

    threads = [threading.Thread(target=stream, args=(n, p), daemon=True) for n, p in procs]
    for t in threads:
        t.start()

    # ── Handle Ctrl+C gracefully ───────────────────────────────────────────
    def shutdown(sig, frame):
        print("\n[NEXUS] Shutting down all services...")
        for _, p in procs:
            p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep alive — restart crashed processes
    while True:
        for name, proc in procs:
            if proc.poll() is not None:
                print(f"[NEXUS] {name} exited with code {proc.returncode}")
        time.sleep(5)


if __name__ == "__main__":
    launch()
