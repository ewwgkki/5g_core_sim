# udm/main.py
# Created by Kai Wang G on 2025-05-23.

import logging
import asyncio
from fastapi import FastAPI
from udm.api.uecm import router as uecm_router
from udm.api.ueau import router as ueau_router
from udm.api.sdm import router as sdm_router
import httpx
from udm import config

# Suppress httpx request-level logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Apply configurable log level
from web.config_store import get_section as _get_section
_log_level = _get_section("log_level") or "INFO"
if isinstance(_log_level, str):
    logging.basicConfig(level=getattr(logging, _log_level.upper(), logging.INFO),
                        format="%(asctime)s [%(levelname)s] %(message)s")

async def register_to_nrf():
    nf_profile = {
        "nfInstanceId": config.UDM_INSTANCE_ID,
        "nfType": "UDM",
        "nfStatus": "REGISTERED",
        "ipv4Addresses": [config.UDM_HOST],
        "fqdn": config.UDM_FQDN,
        "plmnList": [
            {"mcc": config.UDM_MCC, "mnc": config.UDM_MNC}
        ],
        "sNssais": [
            {"sst": 1, "sd": "000001"}
        ],
        "udmInfo": {
            "routingIndicators": [config.UDM_ROUTING_INDICATOR],
            "supiRanges": [
                {"start": config.UDM_SUPI_RANGE_START, "end": config.UDM_SUPI_RANGE_END}
            ],
            "gpsiRanges": [
                {"start": config.UDM_GPSI_RANGE_START, "end": config.UDM_GPSI_RANGE_END}
            ]
        },
        "nfServices": [
            {
                "serviceInstanceId": "nudm-uecm",
                "serviceName": "nudm-uecm",
                "scheme": "http",
                "nfServiceStatus": "REGISTERED",
                "fqdn": config.UDM_FQDN,
                "ipEndPoints": [
                    {"ipv4Address": config.UDM_HOST, "port": config.UDM_PORT, "transport": "TCP"}
                ],
                "versions": [
                    {"apiFullVersion": "1.1.0", "apiVersionInUri": "v1"}
                ]
            },
            {
                "serviceInstanceId": "nudm-sdm",
                "serviceName": "nudm-sdm",
                "scheme": "http",
                "nfServiceStatus": "REGISTERED",
                "fqdn": config.UDM_FQDN,
                "ipEndPoints": [
                    {"ipv4Address": config.UDM_HOST, "port": config.UDM_PORT, "transport": "TCP"}
                ],
                "versions": [
                    {"apiFullVersion": "1.0.0", "apiVersionInUri": "v1"}
                ]
            },
            {
                "serviceInstanceId": "nudm-ueau",
                "serviceName": "nudm-ueau",
                "scheme": "http",
                "nfServiceStatus": "REGISTERED",
                "fqdn": config.UDM_FQDN,
                "ipEndPoints": [
                    {"ipv4Address": config.UDM_HOST, "port": config.UDM_PORT, "transport": "TCP"}
                ],
                "versions": [
                    {"apiFullVersion": "1.0.0", "apiVersionInUri": "v1"}
                ]
            }
        ]
    }
    url = f"{config.NRF_BASE_URI}/nf-instances/{config.UDM_INSTANCE_ID}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.put(url, json=nf_profile)
            if resp.status_code in (200, 201):
                logging.info("UDM successfully registered to NRF.")
                return True
            else:
                logging.warning(f"Failed to register UDM to NRF: {resp.status_code} {resp.text}")
    except Exception as e:
        logging.error(f"Exception during UDM NRF registration: {e}")
    return False

async def wait_and_register():
    registered = False
    while True:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(config.NRF_URI)
                nrf_up = resp.status_code == 200
        except Exception:
            nrf_up = False

        if nrf_up:
            if not registered:
                logging.info("NRF is available, registering UDM...")
                registered = await register_to_nrf()
        else:
            if registered:
                logging.info("NRF became unreachable, will re-register when it comes back...")
            registered = False
        await asyncio.sleep(5)

app = FastAPI(title="UDM - Unified Data Management")

@app.on_event("startup")
async def startup():
    logging.info("UDM service starting...")
    asyncio.create_task(wait_and_register())

@app.on_event("shutdown")
async def shutdown():
    logging.info("UDM service shutting down...")

app.include_router(uecm_router)
app.include_router(ueau_router)
app.include_router(sdm_router)
