# run_amf.py
# Created by Kai Wang G on 2025-05-21.

from utils.path import init_sys_path
init_sys_path()

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("run_amf")

for pkg in ["fastapi", "uvicorn", "httpx"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import uvicorn
from amf import config
from amf.main import app

DEFAULT_HOST = config.AMF_HOST
DEFAULT_PORT = config.AMF_PORT

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    logger.info(f"Starting AMF service: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
