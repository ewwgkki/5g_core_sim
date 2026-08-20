# run_udm.py
# Created by Kai Wang G on 2025-05-23.
import sys
if sys.version_info < (3, 6):
    raise SystemExit("Python 3.6+ required. Run with: python3.6 run_udm.py")

import logging
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

import uvicorn
from utils.path import init_sys_path
init_sys_path()

from udm import config
from udm.main import app

DEFAULT_HOST = config.UDM_HOST
DEFAULT_PORT = config.UDM_PORT

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    print("Starting UDM service: http://{}:{}".format(host, port))
    uvicorn.run(app, host=host, port=port)
