# run_web.py
# Created by Kai Wang G on 2025-05-24.
import sys
if sys.version_info < (3, 6):
    raise SystemExit("Python 3.6+ required. Run with: python3.6 run_web.py")

import os
import subprocess

LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")

def ensure_deps():
    try:
        import fastapi, uvicorn, httpx
    except ImportError:
        req = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        if os.path.isdir(LIB_DIR):
            print("Installing dependencies from lib/ (offline)...")
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                "--no-index", "--find-links", LIB_DIR, "-r", req, "--user"])
        else:
            print("Installing dependencies from PyPI...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req, "--user"])

ensure_deps()

from utils.path import init_sys_path
init_sys_path()

import uvicorn

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    print("Starting Web Console: http://{}:{}".format(host, port))
    uvicorn.run("web.main:app", host=host, port=port, reload=False)
