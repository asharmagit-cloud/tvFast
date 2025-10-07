from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class CityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    state_id: str = Field(..., min_length=24, max_length=24)
    state_name: str = Field(..., max_length=100)
    state_code: str = Field(..., max_length=10)
    is_active: bool = Field(default=True)


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    state_id: Optional[str] = Field(None, min_length=24, max_length=24)
    state_name: Optional[str] = Field(None, max_length=100)
    state_code: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None


class CityResponse(CityBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "name": "Mumbai",
                "state_id": "507f1f77bcf86cd799439011",
                "state_name": "Maharashtra",
                "state_code": "MH",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }


class CityListResponse(BaseModel):
    cities: list[CityResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

    class Config:
        json_schema_extra = {
            "example": {
                "cities": [],
                "total": 0,
                "page": 1,
                "size": 10,
                "has_next": False,
                "has_prev": False
            }
        }
