from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from database import get_database
from models.city import CityModel
from schemas.city import CityCreate, CityUpdate, CityResponse, CityListResponse


def convert_objectids(obj):
    if isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(i) for i in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj


class CityController:
    def __init__(self):
        self.collection_name = "cities"

    async def create_city(self, city_data: CityCreate) -> CityResponse:
        """Create a new city"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Validate state_id
        if not ObjectId.is_valid(city_data.state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        # Check if state exists
        states_collection = db["states"]
        state = await states_collection.find_one({"_id": ObjectId(city_data.state_id)})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State not found"
            )
        
        # Check if city with same name in same state already exists
        existing_city = await collection.find_one({
            "name": city_data.name,
            "state_id": ObjectId(city_data.state_id)
        })
        if existing_city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"City '{city_data.name}' already exists in this state"
            )
        
        # Create city model
        city_dict = city_data.dict()
        city_dict["state_id"] = ObjectId(city_data.state_id)
        city_model = CityModel(**city_dict)
        city_dict = city_model.dict(by_alias=True, exclude={"id"})
        
        # Insert into database
        result = await collection.insert_one(city_dict)
        
        # Fetch the created city
        created_city = await collection.find_one({"_id": result.inserted_id})
        return CityResponse(**created_city)

    async def get_city_by_id(self, city_id: str) -> CityResponse:
        """Get city by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        city = await collection.find_one({"_id": ObjectId(city_id)})
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        return CityResponse(**city)

    async def get_cities(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search: Optional[str] = None,
        state_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> CityListResponse:
        """Get list of cities with pagination and filtering (minimal fields)"""
        db = await get_database()
        collection = db[self.collection_name]

        # Build filter query
        filter_query = {}
        if search:
            filter_query["name"] = {"$regex": search, "$options": "i"}
        if state_id:
            if not ObjectId.is_valid(state_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state ID format"
                )
            filter_query["state_id"] = ObjectId(state_id)
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        # Get total count
        total = await collection.count_documents(filter_query)
        
        # Get cities with pagination
        cursor = collection.find(filter_query).skip(skip).limit(limit)
        cities = await cursor.to_list(length=limit)
        
        city_responses = []
        states_collection = db["states"]
        countries_collection = db["countries"] if "countries" in await db.list_collection_names() else None
        regions_collection = db["regions"] if "regions" in await db.list_collection_names() else None
        for city in cities:
            city = convert_objectids(city)
            # Enrich location names
            if city.get("location") and isinstance(city["location"], list):
                for loc in city["location"]:
                    # Country
                    if loc.get("country") and loc["country"].get("id") and (loc["country"].get("name") is None) and countries_collection is not None:
                        country_doc = await countries_collection.find_one({"_id": ObjectId(loc["country"]["id"])} )
                        if country_doc:
                            loc["country"]["name"] = country_doc.get("name")
                    # Region
                    if loc.get("region") and loc["region"].get("id") and (loc["region"].get("name") is None) and regions_collection is not None:
                        region_doc = await regions_collection.find_one({"_id": ObjectId(loc["region"]["id"])} )
                        if region_doc:
                            loc["region"]["name"] = region_doc.get("name")
                    # State
                    if loc.get("state") and loc["state"].get("id") and (loc["state"].get("name") is None):
                        state_doc = await states_collection.find_one({"_id": ObjectId(loc["state"]["id"])} )
                        if state_doc:
                            loc["state"]["name"] = state_doc.get("name")
            # ...existing code for state_id, state_name, city_response_dict, etc...
            city_id = str(city.get("_id")) if city.get("_id") else None
            state_id_val = city.get("state_id")
            if not state_id_val and city.get("location"):
                try:
                    state_id_val = city["location"][0]["state"]["id"]
                except (KeyError, IndexError, TypeError):
                    state_id_val = None
            state_id_str = str(state_id_val) if state_id_val else None
            name = city.get("name")
            state_name = None
            if state_id_str:
                state_doc = await states_collection.find_one({"_id": ObjectId(state_id_str)})
                if state_doc:
                    state_name = state_doc.get("name")
            city_response_dict = {
                "id": city_id,
                "name": name,
                "state_id": state_id_str,
                "is_active": city.get("is_active", True),
                "location": city.get("location"),
                "greetingText": city.get("greetingText"),
                "tagLine": city.get("tagLine"),
                "languages": city.get("languages"),
                "description": city.get("description"),
                "images": city.get("images"),
                "emergencyContacts": city.get("emergencyContacts"),
                "safetyInformation": city.get("safetyInformation"),
                "travelTips": city.get("travelTips"),
                "experiences": city.get("experiences"),
                "trending": city.get("trending")
            }
            if state_name:
                city_response_dict["state_name"] = state_name
            if not all([city_id, state_id_str, name]):
                continue
            city_responses.append(CityResponse(**city_response_dict))

        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = (skip + limit) < total
        has_prev = skip > 0
        
        return CityListResponse(
            cities=city_responses,
            total=total,
            page=page,
            size=limit,
            has_next=has_next,
            has_prev=has_prev
        )

    async def update_city(self, city_id: str, city_data: CityUpdate) -> CityResponse:
        """Update city by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        # Check if city exists
        existing_city = await collection.find_one({"_id": ObjectId(city_id)})
        if not existing_city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        # Validate state_id if provided
        if city_data.state_id:
            if not ObjectId.is_valid(city_data.state_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state ID format"
                )
            
            # Check if state exists
            states_collection = db["states"]
            state = await states_collection.find_one({"_id": ObjectId(city_data.state_id)})
            if not state:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="State not found"
                )
        
        # Check if new name conflicts with existing city in same state
        if city_data.name:
            state_id_to_check = ObjectId(city_data.state_id) if city_data.state_id else existing_city["state_id"]
            name_conflict = await collection.find_one({
                "name": city_data.name,
                "state_id": state_id_to_check,
                "_id": {"$ne": ObjectId(city_id)}
            })
            if name_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"City '{city_data.name}' already exists in this state"
                )
        
        # Prepare update data
        update_data = {k: v for k, v in city_data.dict().items() if v is not None}
        if update_data:
            if "state_id" in update_data:
                update_data["state_id"] = ObjectId(update_data["state_id"])
            update_data["updated_at"] = CityModel().updated_at
        
        # Update city
        await collection.update_one(
            {"_id": ObjectId(city_id)},
            {"$set": update_data}
        )
        
        # Return updated city
        updated_city = await collection.find_one({"_id": ObjectId(city_id)})
        return CityResponse(**updated_city)

    async def delete_city(self, city_id: str) -> dict:
        """Delete city by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        # Check if city exists
        existing_city = await collection.find_one({"_id": ObjectId(city_id)})
        if not existing_city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        # Check if city has places
        places_collection = db["places"]
        places_count = await places_collection.count_documents({"city_id": ObjectId(city_id)})
        if places_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete city. It has {places_count} places associated with it."
            )
        
        # Delete city
        await collection.delete_one({"_id": ObjectId(city_id)})
        
        return {"message": "City deleted successfully"}

    async def get_cities_by_state(self, state_id: str) -> List[CityResponse]:
        """Get all cities by state ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        cursor = collection.find({"state_id": ObjectId(state_id), "is_active": True})
        cities = await cursor.to_list(length=None)
        
        return [CityResponse(**city) for city in cities]
