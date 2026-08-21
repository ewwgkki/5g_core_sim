# run_web.py
# Created by Kai Wang G on 2025-05-24.
import sys
if sys.version_info < (3, 6):
    raise SystemExit("Python 3.6+ required. Run with: python3.6 run_web.py")

import os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import utils.contextvars_stub  # noqa - must be before any other import on Python 3.6
from utils.bootstrap import ensure_deps
ensure_deps()

from utils.path import init_sys_path
init_sys_path()

from utils.serve import serve

if __name__ == "__main__":
    from web.config_store import get_section
    _web = get_section("web") or {}
    host = sys.argv[1] if len(sys.argv) > 1 else _web.get("host", "0.0.0.0")
    port = int(sys.argv[2]) if len(sys.argv) > 2 else int(_web.get("port", 8080))
    print("Starting Web Console: http://{}:{}".format(host, port))
    serve("web.main:app", host=host, port=port)
