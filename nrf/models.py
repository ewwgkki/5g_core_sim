#
#   models.py
# 
# 
#   Created by Kai Wang G on 2025-05-20.
# 


from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class NFType(str, Enum):
    AMF = "AMF"
    UDM = "UDM"
    LMF = "LMF"
    GMLC = "GMLC"
    NRF = "NRF"
    SMF = "SMF"
    PCF = "PCF"
    AUSF = "AUSF"
    UPF = "UPF"
    NEF = "NEF"
    NSSF = "NSSF"
    BSF = "BSF"
    CHF = "CHF"
    SCP = "SCP"
    SEPP = "SEPP"
    OTHER = "OTHER"

class NFService(BaseModel):
    serviceName: str
    version: str

class NFInstance(BaseModel):
    nfInstanceId: str
    nfType: NFType
    ipv4Addr: str
    port: int
    fqdn: Optional[str] = None
    services: List[NFService] = []
    status: str = "REGISTERED"
    registrationTime: Optional[str] = None

