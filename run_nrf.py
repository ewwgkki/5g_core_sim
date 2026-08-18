# run_nrf.py
# Created by Kai Wang G on 2025-05-20.

import subprocess
import sys
from nrf import config

for pkg in ["fastapi", "uvicorn", "httpx"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import uvicorn

DEFAULT_HOST = config.NRF_HOST
DEFAULT_PORT = config.NRF_PORT

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    print(f"Starting NRF service: http://{host}:{port}")
    uvicorn.run("nrf.main:app", host=host, port=port, reload=True)
