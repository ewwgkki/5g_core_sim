# amf/config.py
#  Created by Kai Wang G on 2025-05-21.

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web.config_store import get_section

_amf = get_section("amf")
_lmf = get_section("lmf")
_nrf = get_section("nrf")

AMF_HOST        = _amf.get("host", "127.0.0.1")
AMF_PORT        = _amf.get("port", 9999)
AMF_FQDN        = _amf.get("fqdn", "fe-1.amf.5gc.mnc080.mcc240.3gppnetwork.org")
AMF_INSTANCE_ID = _amf.get("instance_id", "F63F4247-CC1F-46BC-A903-52184744F029")

LMF_HOST = _lmf.get("host", "127.0.0.1")
LMF_PORT = _lmf.get("port", 9988)

NRF_HOST = _nrf.get("host", "127.0.0.1")
NRF_PORT = _nrf.get("port", 8000)
NRF_URI  = f"http://{NRF_HOST}:{NRF_PORT}/nnrf-nfm/v1/nf-instances"
