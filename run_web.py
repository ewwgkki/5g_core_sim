# run_web.py
# Created by Kai Wang G on 2025-05-24.
import sys
if sys.version_info < (3, 6):
    raise SystemExit("Python 3.6+ required. Run with: python3.6 run_web.py")

import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in __import__('sys').path:
    __import__('sys').path.insert(0, ROOT)

from utils.bootstrap import ensure_deps
ensure_deps()

from utils.path import init_sys_path
init_sys_path()

import uvicorn

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    print("Starting Web Console: http://{}:{}".format(host, port))
    uvicorn.run("web.main:app", host=host, port=port, reload=False)
