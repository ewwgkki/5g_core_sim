# amf/api/namf_comm.py
# Namf_Communication service (NLs reference point: LMF -> AMF)
# Simulates UE LPP responses back to LMF
# Resolves pending GMLC sessions when LMF returns final location
# Ref: 3GPP TS 29.518

import logging
import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from amf import config, session

router = APIRouter()

# ── LMF -> AMF: N1N2MessageTransfer ──────────────────────────────────────────
# LMF sends LPP/NRPPa downlink message to UE through AMF.
# AMF simulates UE response and posts it back to LMF via N1MessageNotify.
@router.post("/namf-comm/v1/{ueContextId}/n1-n2-messages")
async def n1_n2_message_transfer(ueContextId: str, body: dict):
    correlation_id  = body.get("lcsCorrelationId", "")
    lmf_callback    = body.get("lmfCallbackUri", "")
    n1_msg          = body.get("n1MessageContainer", {})
    lpp_type        = n1_msg.get("lppMessageType", "") if n1_msg else ""

    logging.info(f"[{ueContextId}] N1N2MessageTransfer from LMF — lppType={lpp_type} correlationId={correlation_id}")

    # Store LMF callback URI in the pending session
    if correlation_id and correlation_id in session.pending:
        if lmf_callback:
            session.pending[correlation_id]["lmf_callback_uri"] = lmf_callback

    # Simulate UE response based on LPP message type
    ue_response = _simulate_ue_response(lpp_type, ueContextId)
    if ue_response and lmf_callback:
        await _notify_lmf(lmf_callback, ueContextId, correlation_id, ue_response)

    return {"cause": "N1_N2_TRANSFER_INITIATED"}


# ── LMF -> AMF: DetermineLocation final response ──────────────────────────────
# LMF posts the final location result back to AMF.
# AMF resolves the pending GMLC session.
@router.post("/namf-comm/v1/{ueContextId}/location-result")
async def location_result(ueContextId: str, body: dict):
    correlation_id = body.get("lcsCorrelationId", "")
    logging.info(f"[{ueContextId}] Final location result received from LMF — correlationId={correlation_id}")

    if correlation_id and correlation_id in session.pending:
        session.pending[correlation_id]["result"] = body
        session.pending[correlation_id]["event"].set()
        return JSONResponse(content={"status": "ok"}, status_code=200)

    logging.warning(f"[{ueContextId}] No pending session found for correlationId={correlation_id}")
    return JSONResponse(content={"status": "no_session"}, status_code=404)


# ── LMF -> AMF: N1MessageNotify (uplink LPP from UE) ─────────────────────────
@router.post("/namf-comm/v1/{ueContextId}/n1-message-notify", status_code=204)
async def n1_message_notify(ueContextId: str, body: dict):
    logging.info(f"[{ueContextId}] N1MessageNotify received (UL LPP from UE)")
    return None


# ── LMF -> AMF: N2InfoNotify (uplink NRPPa from gNodeB) ──────────────────────
@router.post("/namf-comm/v1/{ueContextId}/n2-info-notify", status_code=204)
async def n2_info_notify(ueContextId: str, body: dict):
    logging.info(f"[{ueContextId}] N2InfoNotify received (UL NRPPa from gNodeB)")
    return None


# ── NI-LR: AMF -> GMLC EventNotify ───────────────────────────────────────────
async def send_event_notify_to_gmlc(notified_pos_info: dict):
    from web.config_store import get_section
    gmlc_cfg  = get_section("gmlc")
    gmlc_host = gmlc_cfg.get("host", "")
    gmlc_port = gmlc_cfg.get("port", 0)

    if not gmlc_host or not gmlc_port:
        logging.warning("GMLC address not configured, skipping EventNotify")
        return

    url = f"http://{gmlc_host}:{gmlc_port}/gmlc/namf-loc/v1/EventNotify"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=notified_pos_info)
            if resp.status_code == 204:
                logging.info("EventNotify sent to GMLC successfully")
            else:
                logging.warning(f"EventNotify to GMLC returned {resp.status_code}: {resp.text}")
    except Exception as e:
        logging.error(f"Failed to send EventNotify to GMLC: {e}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _simulate_ue_response(lpp_type: str, ueContextId: str) -> dict | None:
    """Return a simulated UE LPP response based on the incoming LPP message type."""
    if lpp_type == "RequestCapabilities":
        logging.info(f"[{ueContextId}] Simulating UE LPP ProvideCapabilities")
        return {
            "lppMessageType": "ProvideCapabilities",
            "commonIEsProvideCapabilities": {},
            "gnss-SupportList": [
                {"gnss-ID": "gps", "adr-Support": True, "velocityMeasurementSupport": True}
            ],
            "ecid-ProvideCapabilities": {"rsrpSup": True}
        }

    if lpp_type == "ProvideAssistanceData":
        # No UE response needed for assistance data delivery
        return None

    if lpp_type == "RequestLocationInformation":
        logging.info(f"[{ueContextId}] Simulating UE LPP ProvideLocationInformation")
        return {
            "lppMessageType": "ProvideLocationInformation",
            "commonIEsProvideLocationInformation": {},
            "gnss-ProvideLocationInformation": {
                "gnss-SignalMeasurementInformation": {
                    "measurementReferenceTime": {},
                    "gnss-MeasurementList": [
                        {
                            "gnss-ID": "gps",
                            "gnss-SgnMeasList": [
                                {
                                    "gnss-SignalID": 0,
                                    "gnss-MeasurementList": [
                                        {"svID": {"satellite-id": 1}, "cNo": 35,
                                         "mpathDet": "notUsed", "carrierQualInd": 0,
                                         "codePhase": 100, "integerCodePhase": 0,
                                         "codePhaseRMSError": 3, "pseuDoRange": 20000000,
                                         "pseuDoRangeRMSError": 5}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }

    logging.info(f"[{ueContextId}] No simulated UE response for lppType={lpp_type}")
    return None


async def _notify_lmf(callback_uri: str, ueContextId: str, correlation_id: str, ue_response: dict):
    """POST simulated UE response back to LMF via N1MessageNotify."""
    url = f"{callback_uri}/namf-comm/v1/{ueContextId}/n1-message-notify"
    payload = {
        "lcsCorrelationId":  correlation_id,
        "n1MessageContainer": ue_response,
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload)
            logging.info(f"[{ueContextId}] N1MessageNotify sent to LMF — status={resp.status_code}")
    except Exception as e:
        logging.error(f"[{ueContextId}] Failed to send N1MessageNotify to LMF: {e}")
