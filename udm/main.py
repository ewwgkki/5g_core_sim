# udm/main.py
# Created by Kai Wang G on 2025-05-23.

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from udm.api.uecm import router as uecm_router
from udm.api.ueau import router as ueau_router
from udm.api.sdm import router as sdm_router
import httpx
from udm import config

async def register_to_nrf():
    nf_profile = {
        "nfInstanceId": config.UDM_INSTANCE_ID,
        "nfType": "UDM",
        "status": "REGISTERED",
        "ipv4Addr": config.UDM_HOST,
        "port": config.UDM_PORT,
        "services": [
            {"serviceName": "nudm-uecm", "version": "v1"},
            {"serviceName": "nudm-ueau", "version": "v1"},
            {"serviceName": "nudm-sdm",  "version": "v1"}
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("UDM service starting...")
    asyncio.create_task(wait_and_register())
    yield
    logging.info("UDM service shutting down...")

app = FastAPI(
    title="UDM - Unified Data Management",
    lifespan=lifespan
)

app.include_router(uecm_router)
app.include_router(ueau_router)
app.include_router(sdm_router)
