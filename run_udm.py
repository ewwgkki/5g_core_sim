# run_udm.py
# Created by Kai Wang G on 2025-05-23.

import logging
import subprocess
import sys

for pkg in ["fastapi", "uvicorn", "httpx"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

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
    print(f"Starting UDM service: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
