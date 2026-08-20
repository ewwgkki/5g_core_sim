# nrf/main.py
# Created by Kai Wang G on 2025-05-20.

from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from nrf.models import NFInstance, NFType

app = FastAPI(title="NRF - Network Repository Function")

nf_registry = {}  # keyed by nfInstanceId

@app.put("/nnrf-nfm/v1/nf-instances/{nfInstanceId}", status_code=201)
def register_or_update_nf(nfInstanceId: str, nf_instance: NFInstance):
    nf_instance.nfInstanceId = nfInstanceId
    if nf_instance.registrationTime is None:
        existing = nf_registry.get(nfInstanceId)
        nf_instance.registrationTime = (
            existing.registrationTime if existing
            else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    nf_registry[nfInstanceId] = nf_instance
    return nf_instance

@app.post("/nnrf-nfm/v1/nf-instances")
def register_nf_legacy(nf_instance: NFInstance):
    """Legacy POST endpoint for backward compatibility."""
    nfInstanceId = nf_instance.nfInstanceId
    if nf_instance.registrationTime is None:
        existing = nf_registry.get(nfInstanceId)
        nf_instance.registrationTime = (
            existing.registrationTime if existing
            else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    nf_registry[nfInstanceId] = nf_instance
    return {"result": "NF registered successfully."}

@app.delete("/nnrf-nfm/v1/nf-instances/{nfInstanceId}", status_code=204)
def deregister_nf(nfInstanceId: str):
    if nfInstanceId not in nf_registry:
        raise HTTPException(status_code=404, detail="NF instance not found")
    del nf_registry[nfInstanceId]

@app.get("/nnrf-nfm/v1/nf-instances", response_model=List[NFInstance])
def query_nf_instances(target_nf_type: Optional[NFType] = Query(None, alias="target-nf-type")):
    instances = list(nf_registry.values())
    if target_nf_type:
        instances = [nf for nf in instances if nf.nfType == target_nf_type]
    return instances

@app.get("/nnrf-disc/v1/nf-instances", response_model=List[NFInstance])
def discover_nf_instances(
    target_nf_type: NFType = Query(..., alias="target-nf-type"),
    requester_nf_type: NFType = Query(..., alias="requester-nf-type")
):
    return [nf for nf in nf_registry.values() if nf.nfType == target_nf_type]
