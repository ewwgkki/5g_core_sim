# udm/api/uecm.py
# GMLC-UDM interface — returns AMF registration info for a given MSISDN or IMEI

from fastapi import APIRouter
from fastapi.responses import Response
from web.config_store import get_section

router = APIRouter()

@router.get("/nudm-uecm/v1/msisdn-{number}/registrations/amf-3gpp-access")
async def get_amf_by_msisdn(number: str):
    return _amf_response()

@router.get("/nudm-uecm/v1/imei-{imei}/registrations/amf-3gpp-access")
async def get_amf_by_imei(imei: str):
    return _amf_response()

def _amf_response() -> Response:
    d = get_section("udm").get("static_data", {})
    imei     = d.get("imei", "")
    imsi     = d.get("imsi", "")
    amf_id   = d.get("amf_id", "")
    mcc      = d.get("mcc", "")
    mnc      = d.get("mnc", "")
    inst_id  = d.get("amf_instance_id", "")
    cb_host  = d.get("dereg_callback_host", "")
    cb_port  = d.get("dereg_callback_port", 8080)
    cb_uri   = f"http://{cb_host}:{cb_port}/callbacks/nudm-uecm/v1/imsi-{imsi}/deregistration-notification"

    xml = f"""<IMEI>
{imei}
</IMEI>
<IMSI>
{imsi}
</IMSI>
<AMF>
    <AMFInstanceId>
    {inst_id}
    </AMFInstanceId>
    <DEREG_CALLBACK_URI>
    {cb_uri}
    </DEREG_CALLBACK_URI>
    <Guami>
        <AmfId>
        {amf_id}
        </AmfId>
        <PlmnId>
            <Mcc>
            {mcc}
            </Mcc>
            <Mnc>
            {mnc}
            </Mnc>
        </PlmnId>
    </Guami>
</AMF>"""
    return Response(content=xml.strip(), media_type="application/xml")
