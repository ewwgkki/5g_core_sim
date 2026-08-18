# run_web.py
# Created by Kai Wang G on 2025-05-24.

import sys
import subprocess

for pkg in ["fastapi", "uvicorn", "httpx"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

from utils.path import init_sys_path
init_sys_path()

import uvicorn

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    print(f"Starting Web Console: http://{host}:{port}")
    uvicorn.run("web.main:app", host=host, port=port, reload=False)
