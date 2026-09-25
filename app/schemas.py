from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

def _clean_str(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("cannot be blank")
    return v

class AddressCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=80)
    country: str = Field(..., min_length=1, max_length=80)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    @field_validator("name", "street", "city", "country")
    @classmethod
    def not_blank(cls, v):
        return _clean_str(v)

class AddressUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    street: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=80)
    country: Optional[str] = Field(None, min_length=1, max_length=80)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    @field_validator("name", "street", "city", "country")
    @classmethod
    def not_blank(cls, v):
        if v is None:
            return v
        return _clean_str(v)

class AddressOut(AddressCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NearbyOut(AddressOut):
    distance_km: float
