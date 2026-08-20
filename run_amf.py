# run_amf.py
# Created by Kai Wang G on 2025-05-21.
import sys
if sys.version_info < (3, 6):
    raise SystemExit("Python 3.6+ required. Run with: python3.6 run_amf.py")

import os
import sys
import logging

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.bootstrap import ensure_deps
ensure_deps()

import uvicorn
from amf import config
from amf.main import app

DEFAULT_HOST = config.AMF_HOST
DEFAULT_PORT = config.AMF_PORT

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    print("Starting AMF service: http://{}:{}".format(host, port))
    uvicorn.run(app, host=host, port=port)
