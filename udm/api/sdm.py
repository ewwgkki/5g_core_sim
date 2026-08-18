# udm/api/sdm.py
# UDM subscription data interface (3GPP TS 29.503)

from fastapi import APIRouter
from web.config_store import get_section

router = APIRouter()

@router.get("/nudm-sdm/v1/{supi}/nssai")
async def get_nssai(supi: str):
    d = get_section("udm").get("static_data", {})
    mcc = d.get("mcc", "")
    mnc = d.get("mnc", "")
    return {
        "supi": supi,
        "nssai": {
            "defaultSingleNssais": [
                {"sst": 1, "sd": "000001"}
            ],
            "singleNssais": [
                {"sst": 1, "sd": "000001"},
                {"sst": 2, "sd": "000002"}
            ]
        },
        "plmnId": {"mcc": mcc, "mnc": mnc}
    }

@router.get("/nudm-sdm/v1/{supi}/am-data")
async def get_am_data(supi: str):
    d = get_section("udm").get("static_data", {})
    mcc = d.get("mcc", "")
    mnc = d.get("mnc", "")
    return {
        "supi": supi,
        "gpsis": [f"msisdn-{d.get('msisdn', '')}"],
        "subscribedUeAmbr": {
            "uplink": "1 Gbps",
            "downlink": "1 Gbps"
        },
        "nssai": {
            "defaultSingleNssais": [{"sst": 1, "sd": "000001"}]
        },
        "plmnId": {"mcc": mcc, "mnc": mnc}
    }

@router.get("/nudm-sdm/v1/{supi}/smf-select-data")
async def get_smf_select_data(supi: str):
    d = get_section("udm").get("static_data", {})
    mcc = d.get("mcc", "")
    mnc = d.get("mnc", "")
    return {
        "supi": supi,
        "subscribedSnssaiInfos": {
            "01-000001": {
                "dnnInfos": [
                    {"dnn": "internet", "defaultDnnIndicator": True}
                ]
            }
        },
        "plmnId": {"mcc": mcc, "mnc": mnc}
    }
