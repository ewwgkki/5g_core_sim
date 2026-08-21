# utils/bootstrap.py
import os
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_BASE = os.path.join(ROOT, "lib")
LIB_DIR = os.path.join(LIB_BASE, "py36") if sys.version_info < (3, 8) else os.path.join(LIB_BASE, "py38+")
# Fallback to lib/ root if subdirectories don't exist (backward compat)
if not os.path.isdir(LIB_DIR):
    LIB_DIR = LIB_BASE
REQ_LEGACY = os.path.join(ROOT, "requirements.txt")          # Python 3.6, offline
REQ_MODERN = os.path.join(ROOT, "requirements-modern.txt")   # Python 3.8+, PyPI

IS_LEGACY = sys.version_info < (3, 8)


def _inject_pip_whl():
    matches = glob.glob(os.path.join(LIB_DIR, "pip-*.whl"))
    if not matches:
        raise SystemExit("ERROR: pip not installed and lib/pip-*.whl not found.")
    whl = sorted(matches)[-1]
    if whl not in sys.path:
        sys.path.insert(0, whl)
    print("Bootstrapped pip from: " + os.path.basename(whl))


def _run_pip(args):
    from pip._internal.cli.main import main as pip_main
    rc = pip_main(args)
    if rc != 0:
        raise SystemExit("pip install failed with exit code " + str(rc))


def _reload_site():
    import importlib, site
    importlib.reload(site)
    paths = site.getsitepackages() + [site.getusersitepackages()]
    for path in paths:
        if path not in sys.path:
            sys.path.insert(0, path)


def ensure_deps():
    if sys.version_info < (3, 7):
        try:
            import aiocontextvars  # noqa
        except ImportError:
            pass

    try:
        import fastapi, httpx, aiofiles  # noqa
        from hypercorn.asyncio import serve as _hc_serve  # noqa
        return
    except (ImportError, AttributeError):
        pass

    if IS_LEGACY:
        # Python 3.6/3.7: install from lib/ offline
        try:
            import pip
        except ImportError:
            _inject_pip_whl()
        print("Installing dependencies from lib/ (offline, legacy mode)...")
        _run_pip([
            "install", "--no-index",
            "--find-links", LIB_DIR,
            "--no-deps",
            "--force-reinstall",
            "-r", REQ_LEGACY,
            "--user"
        ])
        _reload_site()
        if sys.version_info < (3, 7):
            try:
                import aiocontextvars  # noqa
            except ImportError:
                pass
    else:
        # Python 3.8+: install from PyPI
        print("Installing dependencies from PyPI (modern mode)...")
        _run_pip(["install", "-r", REQ_MODERN, "--user"])
        _reload_site()
