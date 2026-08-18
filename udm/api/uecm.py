# Created by Kai on May-23 for GMLC-UDM interface
# udm/api/uecm.py

from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()

@router.get("/nudm-uecm/v1/msisdn-{number}/registrations/amf-3gpp-access")
async def get_amf_by_msisdn(number: str):
    return generate_amf_response(number, by="msisdn")

@router.get("/nudm-uecm/v1/imei-{imei}/registrations/amf-3gpp-access")
async def get_amf_by_imei(imei: str):
    return generate_amf_response(imei, by="imei")

def generate_amf_response(identifier: str, by: str) -> Response:
    imei = "13536832400072431"
    imsi = "1240801000000059"
    amf_id = "010041"
    mcc = "240"
    mnc = "80"
    instance_id = "f430f3a5-00fa-48fd-ad65-5ec01a66fb76"
    callback_uri = f"http://10.97.115.43:8080/callbacks/nudm-uecm/v1/imsi-{imsi}/deregistration-notification"

    xml_content = f"""
<IMEI>
{imei if by == "imei" else imei}
</IMEI>
<IMSI>
{imsi}
</IMSI>
<AMF>
    <AMFInstanceId>
    {instance_id}
    </AMFInstanceId>
    <DEREG_CALLBACK_URI>
    {callback_uri}
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
</AMF>
"""
    return Response(content=xml_content.strip(), media_type="application/xml")
