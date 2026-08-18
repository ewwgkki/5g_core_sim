# nrf/main.py
# Created by Kai Wang G on 2025-05-20.

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from nrf.models import NFInstance, NFType

app = FastAPI(title="NRF - Network Repository Function")

nf_registry: List[NFInstance] = []

@app.post("/nnrf-nfm/v1/nf-instances")
def register_nf(nf_instance: NFInstance):
    for nf in nf_registry:
        if nf.nfInstanceId == nf_instance.nfInstanceId:
            raise HTTPException(status_code=400, detail="NF already registered.")
    nf_registry.append(nf_instance)
    return {"result": "NF registered successfully."}

@app.get("/nnrf-nfm/v1/nf-instances", response_model=List[NFInstance])
def query_nf_instances(target_nf_type: Optional[NFType] = Query(None, alias="target-nf-type")):
    if target_nf_type is None:
        return nf_registry
    return [nf for nf in nf_registry if nf.nfType == target_nf_type]

@app.get("/nnrf-disc/v1/nf-instances", response_model=List[NFInstance])
def discover_nf_instances(
    target_nf_type: NFType = Query(..., alias="target-nf-type"),
    requester_nf_type: NFType = Query(..., alias="requester-nf-type")
):
    return [nf for nf in nf_registry if nf.nfType == target_nf_type]
