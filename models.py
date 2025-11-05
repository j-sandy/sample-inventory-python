from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import uuid

class User(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    session_token: str

class Item(BaseModel):
    name: str
    item_code: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image: Optional[str] = None
    description: Optional[str] = None
    quantity: int = Field(gt=0)
    procurement_date: date
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop",
                "item_code": "LAP001",
                "image": "http://example.com/laptop.jpg",
                "description": "High performance laptop",
                "quantity": 10,
                "procurement_date": "2023-01-15",
                "manufacturing_date": "2022-12-01",
                "expiry_date": None
            }
        }
