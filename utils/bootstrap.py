# utils/bootstrap.py
# Offline-first dependency installer.
# Bootstraps pip from lib/pip-*.whl if pip is not installed,
# then installs all dependencies from lib/ using pip's Python API.

import os
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_DIR = os.path.join(ROOT, "lib")
REQ = os.path.join(ROOT, "requirements.txt")


def _inject_pip_whl():
    pattern = os.path.join(LIB_DIR, "pip-*.whl")
    matches = glob.glob(pattern)
    if not matches:
        raise SystemExit("ERROR: pip not installed and lib/pip-*.whl not found.")
    whl = sorted(matches)[-1]
    if whl not in sys.path:
        sys.path.insert(0, whl)
    print("Bootstrapped pip from: " + os.path.basename(whl))


def ensure_deps():
    try:
        import fastapi, uvicorn, httpx
        return
    except ImportError:
        pass

    if not os.path.isdir(LIB_DIR):
        if sys.version_info >= (3, 7):
            req_online = os.path.join(ROOT, "requirements-online.txt")
            req_file = req_online if os.path.exists(req_online) else REQ
        else:
            req_file = REQ
        print("lib/ not found, installing from PyPI...")
        _run_pip(["install", "-r", req_file, "--user"])
        return

    # Ensure pip is importable
    try:
        import pip
    except ImportError:
        _inject_pip_whl()

    print("Installing dependencies from lib/ (offline)...")
    _run_pip([
        "install",
        "--no-index",
        "--find-links", LIB_DIR,
        "-r", REQ,
        "--user"
    ])

    # Reload site packages so newly installed modules are importable
    import importlib
    import site
    importlib.reload(site)
    for path in site.getsitepackages() + [site.getusersitepackages()]:
        if path not in sys.path:
            sys.path.insert(0, path)


def _run_pip(args):
    from pip._internal.cli.main import main as pip_main
    rc = pip_main(args)
    if rc != 0:
        raise SystemExit("pip install failed with exit code " + str(rc))
