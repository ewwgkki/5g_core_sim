# amf/main.py
# Created by Kai Wang G on 2025-05-21.

import importlib.util
import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

from amf.api import namf_loc
from amf.api import namf_comm
from amf.api.namf_loc import monitor_lmf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.py")

def load_config(name, path_to_config_py):
    spec = importlib.util.spec_from_file_location(name, path_to_config_py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

config = load_config("config", config_path)

async def register_to_nrf():
    payload = {
        "nfInstanceId": config.AMF_INSTANCE_ID,
        "nfType": "AMF",
        "fqdn": config.AMF_FQDN,
        "ipv4Addr": config.AMF_HOST,
        "port": config.AMF_PORT,
        "status": "REGISTERED",
        "services": [
            {"serviceName": "namf-comm", "version": "v1"},
            {"serviceName": "namf-loc", "version": "v1"}
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(config.NRF_URI, json=payload)
            if response.status_code == 200:
                print(f"{timestamp()} AMF successfully registered to NRF")
            else:
                print(f"{timestamp()} Registration failed: {response.status_code} - {response.text}")
    except httpx.RequestError as e:
        print(f"{timestamp()} Cannot connect to NRF: {e}")

async def wait_and_register(interval=5):
    registered = False
    while True:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(config.NRF_URI)
                if response.status_code == 200:
                    if not registered:
                        print(f"{timestamp()} NRF is up, registering AMF...")
                        await register_to_nrf()
                        registered = True
                else:
                    registered = False
        except httpx.RequestError:
            if registered:
                print(f"{timestamp()} NRF became unreachable, will re-register when it comes back...")
            else:
                print(f"{timestamp()} Waiting for NRF to start...")
            registered = False
        await asyncio.sleep(interval)

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{timestamp()} AMF service starting...")
    try:
        asyncio.create_task(monitor_lmf())
        asyncio.create_task(wait_and_register())
    except Exception as e:
        print(f"{timestamp()} Lifespan error: {e}")
    yield
    print(f"{timestamp()} AMF service shutting down...")

app = FastAPI(
    title="AMF - Access and Mobility Management Function",
    lifespan=lifespan
)

app.include_router(namf_loc.router)
app.include_router(namf_comm.router)

@app.get("/namf-comm/v1/ue-contexts/{ueContextId}")
def get_ue_context(ueContextId: str):
    return {"ueContextId": ueContextId, "status": "active"}
