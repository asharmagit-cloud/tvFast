from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId


class RefId(BaseModel):
    id: Any
    name: Optional[str] = None


class LocationItem(BaseModel):
    country: RefId
    region: RefId


class Description(BaseModel):
    title: Optional[str] = None
    short: Optional[str] = Field(default=None, alias='short')
    overview: Optional[str] = None
    long: Optional[str] = Field(default=None, alias='long')
    history: Optional[str] = None

    class Config:
        populate_by_name = True


class StateBase(BaseModel):
    id: Any = Field(..., alias="_id")
    name: str
    # optional legacy fields for backward-compat
    #code: Optional[str] = None
    #country: Optional[str] = None
    #is_active: Optional[bool] = None
    # new schema fields
    location: Optional[List[LocationItem]] = None
    greetingText: Optional[str] = None
    tagLine: Optional[str] = None
    languages: Optional[List[str]] = None
    description: Optional[Description] = None
    images: Optional[dict] = None
    labels: Optional[List[RefId]] = None
    emergencyContacts: Optional[dict] = None
    safetyInformation: Optional[List[str]] = None
    travelTips: Optional[List[str]] = None
    experiences: Optional[dict] = None
    trending: Optional[dict] = None
    


class StateCreate(StateBase):
    pass


class StateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class StateResponse(StateBase):
    id_plain: Any = Field(default=None, alias="id")
    id: Any = Field(..., alias="_id")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "68dc1021e2dc335296605a38",
                "id": "68dc1021e2dc335296605a38",
                "name": "Maharashtra",
                "location": [
                    {
                        "country": {
                            "id": "68d7f24214fbfc2474738355",
                            "name": "India"
                        },
                        "region": {
                            "id": "68d7f77c14fbfc2474738359",
                            "name": "West India"
                        }
                    }
                ],
                "greetingText": "Welcome to Maharashtra!",
                "tagLine": "Gateway to the Western Ghats",
                "languages": ["Marathi", "Hindi", "English"],
                "description": {
                    "title": "Maharashtra: Land of Culture and Commerce",
                    "short": "A vibrant state blending tradition and modernity.",
                    "overview": "Maharashtra is one of India's most industrialized and culturally rich states...",
                    "long": "From the bustling streets of Mumbai to the serene hills of Lonavala...",
                    "history": "Historically ruled by the Marathas, the state played a pivotal role..."
                },
                "images": {
                    "banner": "https://example.com/banner.jpg",
                    "card": "https://example.com/card.jpg",
                    "others": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
                },
                "labels": [
                    {
                        "id": "68d90c36fc0c58520c6cf223",
                        "name": "Heritage"
                    }
                ],
                "emergencyContacts": {
                    "Police": "100",
                    "Ambulance": "102",
                    "Fire": "101",
                    "Tourist Helpline": "1363",
                    "State Tourism": "1800-120-8040"
                },
                "safetyInformation": [
                    "Avoid isolated areas at night.",
                    "Keep emergency numbers handy.",
                    "Use registered transport services."
                ],
                "travelTips": [
                    "Carry cash for rural areas.",
                    "Respect local customs and dress modestly.",
                    "Try local cuisine like vada pav and misal pav."
                ],
                "experiences": {
                    "Food": [],
                    "Activities": [],
                    "LocalMarkets": [],
                    "Spiritual": [],
                    "Historical": [],
                    "Nature": [],
                    "Cultural": [],
                    "Adventure": [],
                    "Others": []
                },
                "trending": {
                    "places": [],
                    "cities": []
                },
                "createdAt": "2025-09-30T17:15:13.430000",
                "updatedAt": "2025-09-30T17:15:13.430000"
            }
        }


class StateListResponse(BaseModel):
    states: list[StateResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

    class Config:
        json_schema_extra = {
            "example": {
                "states": [],
                "total": 0,
                "page": 1,
                "size": 10,
                "has_next": False,
                "has_prev": False
            }
        }


class StateQuery(BaseModel):
    skip: int = 0
    limit: int = 10
    search: Optional[str] = None
    is_active: Optional[bool] = None


class StateAllQuery(BaseModel):
    skip: int = 0
    limit: int = 10
