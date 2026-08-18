# udm/api/ueau.py
# UDM authentication data interface (3GPP TS 29.503)

from fastapi import APIRouter
from web.config_store import get_section

router = APIRouter()

@router.get("/nudm-ueau/v1/{supi}/security-information")
async def get_security_info(supi: str):
    d = get_section("udm").get("static_data", {})
    imsi = d.get("imsi", "")

    return {
        "supi": supi,
        "authType": "5G_AKA",
        "authenticationVector": {
            "avType": "5G_HE_AKA",
            "rand": "A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6",
            "autn": "B1C2D3E4F5A6B7C8D9E0F1A2B3C4D5E6",
            "xresStar": "C1D2E3F4A5B6C7D8E9F0A1B2C3D4E5F6",
            "kausf": "D1E2F3A4B5C6D7E8F9A0B1C2D3E4F5A6"
        },
        "supi": supi,
        "imsi": imsi,
        "sequenceNumber": {
            "sqn": "000000000001",
            "sqnScheme": "NON_TIME_BASED"
        }
    }
