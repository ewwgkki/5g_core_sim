# run_nrf.py
# Created by Kai Wang G on 2025-05-20.
import sys
if sys.version_info < (3, 6):
    raise SystemExit("Python 3.6+ required. Run with: python3.6 run_nrf.py")

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

from nrf import config
import uvicorn

DEFAULT_HOST = config.NRF_HOST
DEFAULT_PORT = config.NRF_PORT

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    print("Starting NRF service: http://{}:{}".format(host, port))
    uvicorn.run("nrf.main:app", host=host, port=port, reload=False)
