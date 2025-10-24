from pydantic import BaseModel, Field
from typing import Optional, List, Any
from bson import ObjectId


class RefId(BaseModel):
    id: Any
    name: Optional[str] = None


class LocationItem(BaseModel):
    country: RefId
    region: Optional[RefId] = None
    state: Optional[RefId] = None


class Description(BaseModel):
    title: Optional[str] = None
    short: Optional[str] = Field(default=None, alias='short')
    overview: Optional[str] = None
    long: Optional[str] = Field(default=None, alias='long')
    history: Optional[str] = None


    class Config:
        populate_by_name = True


class CityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    state_id: str = Field(..., min_length=24, max_length=24)
    is_active: bool = Field(default=True)
    location: Optional[List[LocationItem]] = None
    greetingText: Optional[str] = None
    tagLine: Optional[str] = None
    languages: Optional[List[str]] = None
    description: Optional[Description] = None
    images: Optional[dict] = None
    emergencyContacts: Optional[dict] = None
    safetyInformation: Optional[List[str]] = None
    travelTips: Optional[List[str]] = None
    experiences: Optional[dict] = None
    trending: Optional[dict] = None


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    state_id: Optional[str] = Field(None, min_length=24, max_length=24)
    is_active: Optional[bool] = None
    location: Optional[List[LocationItem]] = None
    greetingText: Optional[str] = None
    tagLine: Optional[str] = None
    languages: Optional[List[str]] = None
    description: Optional[Description] = None
    images: Optional[dict] = None
    emergencyContacts: Optional[dict] = None
    safetyInformation: Optional[List[str]] = None
    travelTips: Optional[List[str]] = None
    experiences: Optional[dict] = None
    trending: Optional[dict] = None


class CityResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    state_id: Optional[str] = None
    is_active: bool = True
    location: Optional[List[LocationItem]] = None
    greetingText: Optional[str] = None
    tagLine: Optional[str] = None
    languages: Optional[List[str]] = None
    description: Optional[Description] = None
    images: Optional[dict] = None
    emergencyContacts: Optional[dict] = None
    safetyInformation: Optional[List[str]] = None
    travelTips: Optional[List[str]] = None
    experiences: Optional[dict] = None
    trending: Optional[dict] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "name": "Mumbai",
                "state_id": "507f1f77bcf86cd799439011",
                "is_active": True
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
