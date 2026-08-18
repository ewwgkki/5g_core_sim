#
# nrf/config.py
#
#  Created by Kai Wang G on 2025-05-21.
#

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.config_store import get_section

_cfg = get_section("nrf")
NRF_HOST = _cfg.get("host", "127.0.0.1")
NRF_PORT = _cfg.get("port", 8000)
