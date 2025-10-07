from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from typing import Any, List, Optional, Dict
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> Any:
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: Any, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}


# ----- Nested types matching collections.json -----

class RefId(BaseModel):
    id: PyObjectId


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


class Images(BaseModel):
    banner: Optional[str] = None
    card: Optional[str] = None
    others: Optional[List[str]] = None


class LabelRef(BaseModel):
    id: PyObjectId


class Experiences(BaseModel):
    Food: Optional[List[PyObjectId]] = None
    Activities: Optional[List[PyObjectId]] = None
    LocalMarkets: Optional[List[PyObjectId]] = None
    Spiritual: Optional[List[PyObjectId]] = None
    Historical: Optional[List[PyObjectId]] = None
    Nature: Optional[List[PyObjectId]] = None
    Cultural: Optional[List[PyObjectId]] = None
    Adventure: Optional[List[PyObjectId]] = None
    Others: Optional[List[PyObjectId]] = None


class Trending(BaseModel):
    places: Optional[List[PyObjectId]] = None
    cities: Optional[List[PyObjectId]] = None


class StateModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    location: List[LocationItem]
    greetingText: Optional[str] = None
    tagLine: Optional[str] = None
    description: Optional[Description] = None
    languages: Optional[List[str]] = None
    images: Optional[Images] = None
    labels: Optional[List[LabelRef]] = None
    emergencyContacts: Optional[Dict[str, str]] = None
    safetyInformation: Optional[List[str]] = None
    travelTips: Optional[List[str]] = None
    experiences: Optional[Experiences] = None
    trending: Optional[Trending] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
