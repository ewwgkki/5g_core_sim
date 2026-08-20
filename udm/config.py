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
UDM_FQDN        = _udm.get("fqdn", "udm.5gc.mnc080.mcc240.3gppnetwork.org")
UDM_MCC         = _udm.get("mcc", "240")
UDM_MNC         = _udm.get("mnc", "080")
UDM_ROUTING_INDICATOR = _udm.get("routing_indicator", "0000")
UDM_SUPI_RANGE_START  = _udm.get("supi_range_start", "240800000000000")
UDM_SUPI_RANGE_END    = _udm.get("supi_range_end",   "240809999999999")
UDM_GPSI_RANGE_START  = _udm.get("gpsi_range_start", "46700000000")
UDM_GPSI_RANGE_END    = _udm.get("gpsi_range_end",   "46709999999")

NRF_HOST = _nrf.get("host", "127.0.0.1")
NRF_PORT = _nrf.get("port", 8000)
NRF_HOST = _udm.get("nrf_host") or NRF_HOST
_udm_nrf_port = _udm.get("nrf_port")
NRF_PORT = _udm_nrf_port if _udm_nrf_port else NRF_PORT
NRF_BASE_URI = f"http://{NRF_HOST}:{NRF_PORT}/nnrf-nfm/v1"
NRF_URI  = f"{NRF_BASE_URI}/nf-instances"
