from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.state import PyObjectId


class RefId(BaseModel):
    id: PyObjectId


class LocationItem(BaseModel):
    country: RefId
    state: RefId
    city: RefId
    region: RefId


class CityModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    slug: str
    location: List[LocationItem]
    labels: Optional[List[RefId]] = None
    tips: Optional[List[str]] = None
    bestTimeToVisit: Optional[str] = None
    localLegend: Optional[str] = None
    difficultyLevel: Optional[str] = None
    entryInfo: Optional[dict] = None
    images: Optional[dict] = None
    description: Optional[dict] = None
    geo: Optional[dict] = None
    ratings: Optional[dict] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
