# amf/api/namf_comm.py
# Namf_Communication service (NLs reference point: LMF -> AMF)
# Also handles NI-LR EventNotify callback from AMF to GMLC
# Ref: 3GPP TS 29.518

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from amf import config

router = APIRouter()

# ── NLs: LMF -> AMF ──────────────────────────────────────────────────────────
# Namf_Communication_N1N2MessageTransfer
# LMF uses this to send LPP/NRPPa messages to UE through AMF
@router.post("/namf-comm/v1/{ueContextId}/n1-n2-messages", status_code=200)
async def n1_n2_message_transfer(ueContextId: str, body: dict):
    n1_message = body.get("n1MessageContainer")
    n2_info    = body.get("n2InfoContainer")
    logging.info(f"[{ueContextId}] N1N2MessageTransfer received from LMF - n1={bool(n1_message)} n2={bool(n2_info)}")
    # In a real AMF this would forward the LPP/NRPPa message to the UE over NAS/NGAP.
    # In this simulator we acknowledge immediately.
    return {"cause": "N1_N2_TRANSFER_INITIATED"}


# Namf_Communication_N1MessageNotify
# AMF forwards uplink LPP message from UE back to LMF callback URI
@router.post("/namf-comm/v1/{ueContextId}/n1-message-notify", status_code=204)
async def n1_message_notify(ueContextId: str, body: dict):
    logging.info(f"[{ueContextId}] N1MessageNotify received (UL LPP from UE)")
    return None


# Namf_Communication_N2InfoNotify
# AMF forwards uplink NRPPa message from gNodeB back to LMF callback URI
@router.post("/namf-comm/v1/{ueContextId}/n2-info-notify", status_code=204)
async def n2_info_notify(ueContextId: str, body: dict):
    logging.info(f"[{ueContextId}] N2InfoNotify received (UL NRPPa from gNodeB)")
    return None


# ── NI-LR: AMF -> GMLC EventNotify ───────────────────────────────────────────
# AMF pushes emergency positioning result to GMLC
# GMLC listens at: POST /gmlc/namf-loc/v1/EventNotify
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
