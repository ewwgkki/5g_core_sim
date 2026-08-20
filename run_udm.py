# run_udm.py
# Created by Kai Wang G on 2025-05-23.
import sys
if sys.version_info < (3, 6):
    raise SystemExit("Python 3.6+ required. Run with: python3.6 run_udm.py")

import logging
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import utils.contextvars_stub  # noqa
from utils.bootstrap import ensure_deps
ensure_deps()

from utils.serve import serve
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
    print("Starting UDM service: https://{}:{}".format(host, port))
    serve("udm.main:app", host=host, port=port)
