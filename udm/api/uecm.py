# udm/api/uecm.py
# GMLC-UDM interface — returns AMF registration info for a given MSISDN or IMEI

from fastapi import APIRouter
from fastapi.responses import Response
from web.config_store import get_section

router = APIRouter()

@router.get("/nudm-uecm/v1/msisdn-{number}/registrations/amf-3gpp-access")
async def get_amf_by_msisdn(number: str):
    d = get_section("udm").get("static_data", {})
    return _amf_response(
        msisdn=number,
        imei=d.get("imei", ""),
        imsi=d.get("imsi", "")
    )

@router.get("/nudm-uecm/v1/imei-{imei}/registrations/amf-3gpp-access")
async def get_amf_by_imei(imei: str):
    d = get_section("udm").get("static_data", {})
    return _amf_response(
        imei=imei,
        msisdn=d.get("msisdn", ""),
        imsi=d.get("imsi", "")
    )

def _amf_response(imei="", imsi="", msisdn=""):
    d        = get_section("udm").get("static_data", {})
    amf_cfg  = get_section("amf")
    amf_id   = d.get("amf_id", "")
    mcc      = d.get("mcc", "")
    mnc      = d.get("mnc", "")
    inst_id  = amf_cfg.get("instance_id", "")
    cb_host  = d.get("dereg_callback_host", "")
    cb_port  = d.get("dereg_callback_port", 8080)
    cb_uri   = "http://{}:{}/callbacks/nudm-uecm/v1/imsi-{}/deregistration-notification".format(cb_host, cb_port, imsi)

    xml = """<IMEI>
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
</AMF>""".format(imei=imei, imsi=imsi, inst_id=inst_id, cb_uri=cb_uri, amf_id=amf_id, mcc=mcc, mnc=mnc)
    return Response(content=xml.strip(), media_type="application/xml")
