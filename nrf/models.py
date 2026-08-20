#
#   models.py
# 
# 
#   Created by Kai Wang G on 2025-05-20.
# 


from pydantic import BaseModel
from typing import Any, Dict, List, Optional
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
    version: Optional[str] = None
    serviceInstanceId: Optional[str] = None
    scheme: Optional[str] = None
    nfServiceStatus: Optional[str] = None
    fqdn: Optional[str] = None
    ipEndPoints: Optional[List[Dict[str, Any]]] = None
    versions: Optional[List[Dict[str, str]]] = None
    defaultNotificationSubscriptions: Optional[List[Dict[str, Any]]] = None
    supportedFeatures: Optional[str] = None

class NFInstance(BaseModel):
    nfInstanceId: str
    nfType: NFType
    nfStatus: Optional[str] = "REGISTERED"
    ipv4Addr: Optional[str] = None
    ipv4Addresses: Optional[List[str]] = None
    port: Optional[int] = None
    fqdn: Optional[str] = None
    locality: Optional[str] = None
    plmnList: Optional[List[Dict[str, str]]] = None
    sNssais: Optional[List[Dict[str, Any]]] = None
    amfInfo: Optional[Dict[str, Any]] = None
    udmInfo: Optional[Dict[str, Any]] = None
    services: Optional[List[NFService]] = []
    nfServices: Optional[List[NFService]] = None
    status: Optional[str] = "REGISTERED"
    registrationTime: Optional[str] = None

