# src\models\data_models.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class ASInfo(BaseModel):
    asn: str
    company_website: Optional[HttpUrl] = None
    looking_glass: Optional[HttpUrl] = None
    country: Optional[str] = None
    prefixes_originated_all: Optional[int] = None
    prefixes_originated_v4: Optional[int] = None
    prefixes_originated_v6: Optional[int] = None
    rpki_valid_all: Optional[int] = None
    rpki_invalid_all: Optional[int] = None
    bgp_peers_observed_all: Optional[int] = None
    ips_originated_v4: Optional[int] = None
    avg_path_length_all: Optional[float] = None

class CompanyInfo(BaseModel):
    website_url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    contact_emails: List[str] = []
    phone_numbers: List[str] = []
    services: List[str] = []
    address: Optional[str] = None

class ASRecord(BaseModel):
    asn: str
    bgp_info: ASInfo
    company_info: Optional[CompanyInfo] = None
    scraped_at: datetime
