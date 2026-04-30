from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemCreate(BaseModel):
    item_name: Optional [str] = None
    image_path: str

class ItemResponse(BaseModel):
    item_id: int
    item_name: str
    image_path: str
    created_at: datetime

    class Config:
        from_attributes = True
