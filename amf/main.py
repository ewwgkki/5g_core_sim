# amf/main.py
# Created by Kai Wang G on 2025-05-21.

import importlib.util
import os
import asyncio
from datetime import datetime
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
        "nfStatus": "REGISTERED",
        "ipv4Addresses": [config.AMF_HOST],
        "fqdn": config.AMF_FQDN,
        "plmnList": [
            {"mcc": config.AMF_MCC, "mnc": config.AMF_MNC}
        ],
        "sNssais": [
            {"sst": config.AMF_SST, "sd": config.AMF_SD}
        ],
        "amfInfo": {
            "amfRegionId": config.AMF_REGION_ID,
            "amfSetId": config.AMF_SET_ID,
            "guamiList": [
                {
                    "plmnId": {"mcc": config.AMF_MCC, "mnc": config.AMF_MNC},
                    "amfId": config.AMF_ID
                }
            ],
            "taiList": [
                {
                    "plmnId": {"mcc": config.AMF_MCC, "mnc": config.AMF_MNC},
                    "tac": config.AMF_TAC
                }
            ]
        },
        "nfServices": [
            {
                "serviceInstanceId": "namf-comm",
                "serviceName": "namf-comm",
                "scheme": "http",
                "nfServiceStatus": "REGISTERED",
                "fqdn": config.AMF_FQDN,
                "ipEndPoints": [
                    {"ipv4Address": config.AMF_HOST, "port": config.AMF_PORT, "transport": "TCP"}
                ],
                "versions": [
                    {"apiFullVersion": "1.0.0", "apiVersionInUri": "v1"}
                ],
                "defaultNotificationSubscriptions": [
                    {
                        "notificationType": "N1_MESSAGES",
                        "n1MessageClass": "5GMM",
                        "callbackUri": "http://{}:{}/callbacks/namf-comm/v1/n1-message-notify".format(
                            config.AMF_HOST, config.AMF_PORT)
                    }
                ]
            },
            {
                "serviceInstanceId": "namf-loc",
                "serviceName": "namf-loc",
                "scheme": "http",
                "nfServiceStatus": "REGISTERED",
                "fqdn": config.AMF_FQDN,
                "ipEndPoints": [
                    {"ipv4Address": config.AMF_HOST, "port": config.AMF_PORT, "transport": "TCP"}
                ],
                "versions": [
                    {"apiFullVersion": "1.0.0", "apiVersionInUri": "v1"}
                ]
            }
        ]
    }
    if config.AMF_LOCALITY:
        payload["locality"] = config.AMF_LOCALITY
    url = f"{config.NRF_BASE_URI}/nf-instances/{config.AMF_INSTANCE_ID}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.put(url, json=payload)
            if response.status_code in (200, 201):
                print(f"{timestamp()} AMF successfully registered to NRF")
                return True
            else:
                print(f"{timestamp()} Registration failed: {response.status_code} - {response.text}")
    except httpx.RequestError as e:
        print(f"{timestamp()} Cannot connect to NRF: {e}")
    return False

async def wait_and_register(interval=5):
    registered = False
    while True:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(config.NRF_URI)
                nrf_up = response.status_code == 200
        except httpx.RequestError:
            nrf_up = False

        if nrf_up:
            if not registered:
                print(f"{timestamp()} NRF is up, registering AMF...")
                registered = await register_to_nrf()
        else:
            if registered:
                print(f"{timestamp()} NRF became unreachable, will re-register when it comes back...")
            else:
                print(f"{timestamp()} Waiting for NRF to start...")
            registered = False
        await asyncio.sleep(interval)

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

app = FastAPI(title="AMF - Access and Mobility Management Function")

@app.on_event("startup")
async def startup():
    print(f"{timestamp()} AMF service starting...")
    asyncio.create_task(monitor_lmf())
    asyncio.create_task(wait_and_register())

@app.on_event("shutdown")
async def shutdown():
    print(f"{timestamp()} AMF service shutting down...")

app.include_router(namf_loc.router)
app.include_router(namf_comm.router)

@app.get("/namf-comm/v1/ue-contexts/{ueContextId}")
def get_ue_context(ueContextId: str):
    return {"ueContextId": ueContextId, "status": "active"}
