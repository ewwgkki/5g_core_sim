# udm/main.py
# Created by Kai Wang G on 2025-05-23.

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from udm.api.uecm import router as udm_router
import httpx
from udm import config

async def register_to_nrf():
    nf_profile = {
        "nfInstanceId": config.UDM_INSTANCE_ID,
        "nfType": "UDM",
        "status": "REGISTERED",
        "ipv4Addr": config.UDM_HOST,
        "port": config.UDM_PORT,
        "priority": 10,
        "capacity": 100,
        "services": [
            {
                "serviceInstanceId": "nudm-uecm",
                "serviceName": "nudm-uecm",
                "version": "v1",
                "scheme": "http",
                "status": "REGISTERED",
                "ipEndPoints": [{"ipv4Addr": config.UDM_HOST, "port": config.UDM_PORT}]
            }
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(config.NRF_URI, json=nf_profile)
            if resp.status_code == 200:
                logging.info("UDM successfully registered to NRF.")
            else:
                logging.warning(f"Failed to register UDM to NRF. Status: {resp.status_code}, Body: {resp.text}")
    except Exception as e:
        logging.error(f"Exception during UDM registration to NRF: {e}")

async def wait_and_register():
    logging.info("Waiting for NRF to become available...")
    while True:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(config.NRF_URI)
                if resp.status_code == 200:
                    logging.info("NRF is available, registering UDM now...")
                    await register_to_nrf()
                    return
        except Exception:
            logging.info("NRF not reachable yet, retrying in 5 seconds...")
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

app.include_router(udm_router)
