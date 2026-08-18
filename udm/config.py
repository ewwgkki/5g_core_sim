# udm/config.py
#  Created by Kai Wang G on 2025-05-23.

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.config_store import get_section

_udm = get_section("udm")
_nrf = get_section("nrf")

UDM_HOST        = _udm.get("host", "127.0.0.1")
UDM_PORT        = _udm.get("port", 5555)
UDM_INSTANCE_ID = _udm.get("instance_id", "66909D42-05FE-4F2B-98E2-55B7329A2B40")

NRF_HOST = _nrf.get("host", "127.0.0.1")
NRF_PORT = _nrf.get("port", 8000)
NRF_URI  = f"http://{NRF_HOST}:{NRF_PORT}/nnrf-nfm/v1/nf-instances"
