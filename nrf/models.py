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

class NFService(BaseModel):
    serviceName: str
    version: str

class NFInstance(BaseModel):
    nfInstanceId: str
    nfType: NFType
    ipv4Addr: str
    port: int
    fqdn: Optional[str] = None  # 新增字段，非必填
    services: List[NFService]
    status: str  # REGISTERED, ACTIVE, etc.

