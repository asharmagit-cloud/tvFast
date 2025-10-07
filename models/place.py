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


class EntryInfo(BaseModel):
    type: Optional[str] = None
    fee: Optional[str] = None
    duration: Optional[str] = None


class Images(BaseModel):
    banner: Optional[str] = None
    card: Optional[str] = None
    others: Optional[List[str]] = None


class Description(BaseModel):
    overview: Optional[str] = None
    short: Optional[str] = Field(default=None, alias='short')
    long: Optional[str] = Field(default=None, alias='long')
    history: Optional[str] = None

    class Config:
        populate_by_name = True


class Geo(BaseModel):
    type: Optional[str] = None
    coordinates: Optional[List[float]] = None


class Ratings(BaseModel):
    average: Optional[float] = None
    count: Optional[int] = None


class PlaceModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    slug: str
    location: List[LocationItem]
    labels: Optional[List[RefId]] = None
    tips: Optional[List[str]] = None
    bestTimeToVisit: Optional[str] = None
    localLegend: Optional[str] = None
    difficultyLevel: Optional[str] = None
    entryInfo: Optional[EntryInfo] = None
    images: Optional[Images] = None
    description: Optional[Description] = None
    geo: Optional[Geo] = None
    ratings: Optional[Ratings] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
