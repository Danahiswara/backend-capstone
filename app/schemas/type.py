from pydantic import BaseModel
from typing import Optional


class TypeCreate(BaseModel):
    name: str
    komposisi: Optional[str] = None
    farmasi: Optional[str] = None
    distributor: Optional[str] = None
    total_items: Optional[int] = 0


class TypeUpdate(BaseModel):
    name: Optional[str] = None
    komposisi: Optional[str] = None
    farmasi: Optional[str] = None
    distributor: Optional[str] = None
    total_items: Optional[int] = None


class TypeResponse(BaseModel):
    type_id: int
    name: str
    komposisi: Optional[str]
    farmasi: Optional[str]
    distributor: Optional[str]
    total_items: int

    class Config:
        from_attributes = True