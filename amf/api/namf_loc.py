# amf/api/namf_loc.py
# Created by Kai Wang G on 2025-05-22.
# Namf_Location service (NLg reference point: GMLC -> AMF)
# Forwards DetermineLocation to LMF via Nlmf_Location service (NLs reference point)
# Ref: 3GPP TS 29.518 (Namf), 3GPP TS 29.572 (Nlmf)

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import httpx
import logging
from amf import config
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

LMF_AVAILABLE = False

async def monitor_lmf():
    global LMF_AVAILABLE
    prev_status = None

    while True:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"http://{config.LMF_HOST}:{config.LMF_PORT}/nlmf-loc/v1/health")
                LMF_AVAILABLE = resp.status_code == 200
        except Exception:
            LMF_AVAILABLE = False

        if LMF_AVAILABLE != prev_status:
            status_str = "AVAILABLE" if LMF_AVAILABLE else "UNAVAILABLE"
            logging.info(f"LMF status changed: {status_str}")
            prev_status = LMF_AVAILABLE

        await asyncio.sleep(5)

router = APIRouter()

# NLg: GMLC -> AMF (Namf_Location_ProvidePositioningInfo)
# Per 3GPP TS 29.518
@router.post("/namf-loc/v1/{ueContextId}/provide-pos-info")
async def provide_pos_info(ueContextId: str, body: dict):
    supi = body.get("supi")
    gpsi = body.get("gpsi")

    # Build DetermineLocation request per 3GPP TS 29.572 Section 6.1.3.2
    # NLs: AMF -> LMF (Nlmf_Location_DetermineLocation)
    lmf_request = {
        "supi": supi,
        "gpsi": gpsi,
        "ueContextId": ueContextId,
        "lcsClientType": body.get("lcsClientType"),
        "lcsLocation": body.get("lcsLocation"),
        "priority": body.get("priority"),
        "lcsQoS": body.get("lcsQoS"),
        "velocityRequested": body.get("velocityRequested"),
        "lcsSupportedGADShapes": body.get("lcsSupportedGADShapes"),
        "additionalLcsSuppGADShapes": body.get("additionalLcsSuppGADShapes"),
        "servingNrCellId": body.get("servingNrCellId"),
        "lcsCorrelationId": body.get("lcsCorrelationId"),
        "amfId": config.AMF_INSTANCE_ID,
    }

    lmf_endpoint = f"http://{config.LMF_HOST}:{config.LMF_PORT}/nlmf-loc/v1/determine-location"

    if LMF_AVAILABLE:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(lmf_endpoint, json=lmf_request)
                response.raise_for_status()
                lmf_data = response.json()
                logging.info(f"[{ueContextId}] Received DetermineLocation response from LMF")
                return JSONResponse(content={"supi": supi, "gpsi": gpsi, **lmf_data})
        except Exception as e:
            logging.warning(f"[{ueContextId}] LMF DetermineLocation failed, using fallback. Reason: {e}")
            return JSONResponse(content=fallback_location_response(ueContextId, supi, gpsi), status_code=206)
    else:
        logging.warning(f"[{ueContextId}] LMF unavailable, using fallback.")
        return JSONResponse(content=fallback_location_response(ueContextId, supi, gpsi), status_code=206)


def fallback_location_response(ueContextId, supi, gpsi):
    return {
        "ueContextId": ueContextId,
        "supi": supi,
        "gpsi": gpsi,
        "locationEstimate": {
            "shape": "POINT_ALTITUDE_UNCERTAINTY",
            "point": {"lon": -96.83208102986727, "lat": 33.07484112585842},
            "altitude": 1.5,
            "uncertaintyEllipse": {"semiMajor": 3.42, "semiMinor": 1.60, "orientationMajor": 31},
            "uncertaintyAltitude": 0.0,
            "confidence": 95
        },
        "accuracyFulfilmentIndicator": "REQUESTED_ACCURACY_FULFILLED",
        "ageOfLocationEstimate": 0,
        "timestampOfLocationEstimate": datetime.now(timezone.utc).isoformat(),
        "positioningDataList": [
            {"method": "NR_ECID", "mode": "CONVENTIONAL", "usage": "SUCCESS_RESULTS_USED_TO_GENERATE_LOCATION"},
            {"method": "CELLID", "mode": "CONVENTIONAL", "usage": "SUCCESS_RESULTS_NOT_USED"}
        ],
        "ncgi": {
            "plmnId": {"mcc": "240", "mnc": "80"},
            "nrCellId": "927D201E"
        }
    }
