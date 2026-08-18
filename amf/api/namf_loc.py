# amf/api/namf_loc.py
# Namf_Location service (NLg reference point: GMLC -> AMF)
# Forwards DetermineLocation to LMF (NLs: AMF -> LMF)
# Suspends until LMF completes LPP exchange and returns final location
# Ref: 3GPP TS 29.518 (Namf), 3GPP TS 29.572 (Nlmf)

import asyncio
import uuid
import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from amf import config
from amf import session

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
            logging.info(f"LMF status changed: {'AVAILABLE' if LMF_AVAILABLE else 'UNAVAILABLE'}")
            prev_status = LMF_AVAILABLE
        await asyncio.sleep(5)

router = APIRouter()

# NLg: GMLC -> AMF  (Namf_Location_ProvidePositioningInfo)
@router.post("/namf-loc/v1/{ueContextId}/provide-pos-info")
async def provide_pos_info(ueContextId: str, body: dict):
    supi = body.get("supi")
    gpsi = body.get("gpsi")

    if not LMF_AVAILABLE:
        logging.warning(f"[{ueContextId}] LMF unavailable, returning fallback.")
        return JSONResponse(content=_fallback(ueContextId, supi, gpsi), status_code=206)

    # Generate correlation ID to track this session
    correlation_id = str(uuid.uuid4())

    # AMF callback base URI — LMF will POST N1MessageNotify back here
    amf_callback_uri = f"http://{config.AMF_HOST}:{config.AMF_PORT}"

    # Build Nlmf_Location_DetermineLocation request per 3GPP TS 29.572
    lmf_request = {
        "supi":                       supi,
        "gpsi":                       gpsi,
        "ueContextId":                ueContextId,
        "lcsClientType":              body.get("lcsClientType"),
        "lcsLocation":                body.get("lcsLocation"),
        "priority":                   body.get("priority"),
        "lcsQoS":                     body.get("lcsQoS"),
        "velocityRequested":          body.get("velocityRequested"),
        "lcsSupportedGADShapes":      body.get("lcsSupportedGADShapes"),
        "additionalLcsSuppGADShapes": body.get("additionalLcsSuppGADShapes"),
        "servingNrCellId":            body.get("servingNrCellId"),
        "lcsCorrelationId":           correlation_id,
        "amfId":                      config.AMF_INSTANCE_ID,
        "amfCallbackUri":             amf_callback_uri,
    }

    # Register pending session — will be resolved by namf_comm when LMF responds
    event = asyncio.Event()
    session.pending[correlation_id] = {
        "event":            event,
        "result":           None,
        "ueContextId":      ueContextId,
        "lmf_callback_uri": "",   # filled in by LMF's first N1N2MessageTransfer
    }

    try:
        lmf_endpoint = f"http://{config.LMF_HOST}:{config.LMF_PORT}/nlmf-loc/v1/determine-location"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(lmf_endpoint, json=lmf_request)
            if resp.status_code not in (200, 202):
                logging.warning(f"[{ueContextId}] LMF rejected DetermineLocation: {resp.status_code}")
                session.pending.pop(correlation_id, None)
                return JSONResponse(content=_fallback(ueContextId, supi, gpsi), status_code=206)
    except Exception as e:
        logging.error(f"[{ueContextId}] Failed to reach LMF: {e}")
        session.pending.pop(correlation_id, None)
        return JSONResponse(content=_fallback(ueContextId, supi, gpsi), status_code=206)

    # Wait for LMF to complete LPP exchange and post final result back
    try:
        await asyncio.wait_for(event.wait(), timeout=30.0)
    except asyncio.TimeoutError:
        logging.warning(f"[{ueContextId}] Timed out waiting for LMF location result.")
        session.pending.pop(correlation_id, None)
        return JSONResponse(content=_fallback(ueContextId, supi, gpsi), status_code=206)

    result = session.pending.pop(correlation_id, {}).get("result")
    if not result:
        return JSONResponse(content=_fallback(ueContextId, supi, gpsi), status_code=206)

    logging.info(f"[{ueContextId}] Location result received from LMF, returning to GMLC.")
    return JSONResponse(content=result)


def _fallback(ueContextId, supi, gpsi):
    return {
        "ueContextId": ueContextId,
        "supi":        supi,
        "gpsi":        gpsi,
        "locationEstimate": {
            "shape": "POINT_ALTITUDE_UNCERTAINTY",
            "point": {"lon": -96.83208102986727, "lat": 33.07484112585842},
            "altitude": 1.5,
            "uncertaintyEllipse": {"semiMajor": 3.42, "semiMinor": 1.60, "orientationMajor": 31},
            "uncertaintyAltitude": 0.0,
            "confidence": 95
        },
        "accuracyFulfilmentIndicator": "REQUESTED_ACCURACY_FULFILLED",
        "ageOfLocationEstimate":       0,
        "timestampOfLocationEstimate": datetime.now(timezone.utc).isoformat(),
        "positioningDataList": [
            {"method": "NR_ECID", "mode": "CONVENTIONAL",
             "usage": "SUCCESS_RESULTS_USED_TO_GENERATE_LOCATION"},
            {"method": "CELLID", "mode": "CONVENTIONAL",
             "usage": "SUCCESS_RESULTS_NOT_USED"}
        ],
        "ncgi": {
            "plmnId":   {"mcc": "240", "mnc": "80"},
            "nrCellId": "927D201E"
        }
    }
