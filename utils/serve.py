# utils/serve.py - HTTP/2 server via Hypercorn (h2c cleartext or h2 TLS)
import os
import asyncio
import importlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "certs", "cert.pem")
KEY  = os.path.join(ROOT, "certs", "key.pem")


def _tls_enabled():
    try:
        from web.config_store import get_section
        return bool(get_section("tls"))
    except Exception:
        return False


def _ensure_certs():
    if os.path.exists(CERT) and os.path.exists(KEY):
        return
    os.makedirs(os.path.join(ROOT, "certs"), exist_ok=True)
    print("Generating self-signed TLS certificate...")
    os.system(
        'openssl req -x509 -newkey rsa:2048 -keyout "{}" -out "{}" '
        '-days 3650 -nodes -subj "/CN=5g-core-sim"'.format(KEY, CERT)
    )


def serve(app_path, host, port):
    tls = _tls_enabled()

    from hypercorn.config import Config
    from hypercorn.asyncio import serve as hypercorn_serve

    cfg = Config()
    cfg.bind = ["{}:{}".format(host, port)]
    if tls:
        _ensure_certs()
        cfg.certfile = CERT
        cfg.keyfile = KEY
        print("  TLS: enabled (h2)")
    else:
        print("  TLS: disabled (h2c cleartext)")

    mod_name, attr = app_path.rsplit(":", 1)
    app = getattr(importlib.import_module(mod_name), attr)

    asyncio.get_event_loop().run_until_complete(hypercorn_serve(app, cfg))
