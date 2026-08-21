# lib/ — Offline dependency wheels

## py36/
Python 3.6 dependencies for air-gapped deployment.
Used by `requirements.txt` + `bootstrap.py` when running on Python < 3.8.
Includes Hypercorn 0.5.4 (HTTP/2 h2c), pip bootstrap whl, etc.

## py38+/
Python 3.8+ supplementary wheels (optional).
Modern environments typically install from PyPI via `requirements-modern.txt`.
These are only used if PyPI is unavailable on a Python 3.8+ machine.
