from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PlaceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    city_id: str = Field(..., min_length=24, max_length=24)
    city_name: str = Field(..., max_length=100)
    state_id: str = Field(..., min_length=24, max_length=24)
    state_name: str = Field(..., max_length=100)
    state_code: str = Field(..., max_length=10)
    address: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    is_active: bool = Field(default=True)


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    city_id: Optional[str] = Field(None, min_length=24, max_length=24)
    city_name: Optional[str] = Field(None, max_length=100)
    state_id: Optional[str] = Field(None, min_length=24, max_length=24)
    state_name: Optional[str] = Field(None, max_length=100)
    state_code: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class PlaceResponse(PlaceBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439013",
                "name": "Gateway of India",
                "description": "Historic monument in Mumbai",
                "city_id": "507f1f77bcf86cd799439012",
                "city_name": "Mumbai",
                "state_id": "507f1f77bcf86cd799439011",
                "state_name": "Maharashtra",
                "state_code": "MH",
                "address": "Apollo Bandar, Colaba, Mumbai",
                "latitude": 18.9220,
                "longitude": 72.8347,
                "category": "Monument",
                "tags": ["historic", "monument", "tourism"],
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }


class PlaceListResponse(BaseModel):
    places: list[PlaceResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

    class Config:
        json_schema_extra = {
            "example": {
                "places": [],
                "total": 0,
                "page": 1,
                "size": 10,
                "has_next": False,
                "has_prev": False
            }
        }
