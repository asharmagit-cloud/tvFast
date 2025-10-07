from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from database import get_database
from models.place import PlaceModel
from schemas.place import PlaceCreate, PlaceUpdate, PlaceResponse, PlaceListResponse


class PlaceController:
    def __init__(self):
        self.collection_name = "places"

    async def create_place(self, place_data: PlaceCreate) -> PlaceResponse:
        """Create a new place"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Validate city_id and state_id
        if not ObjectId.is_valid(place_data.city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        if not ObjectId.is_valid(place_data.state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        # Check if city exists
        cities_collection = db["cities"]
        city = await cities_collection.find_one({"_id": ObjectId(place_data.city_id)})
        if not city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City not found"
            )
        
        # Check if state exists
        states_collection = db["states"]
        state = await states_collection.find_one({"_id": ObjectId(place_data.state_id)})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State not found"
            )
        
        # Check if place with same name in same city already exists
        existing_place = await collection.find_one({
            "name": place_data.name,
            "city_id": ObjectId(place_data.city_id)
        })
        if existing_place:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Place '{place_data.name}' already exists in this city"
            )
        
        # Create place model
        place_dict = place_data.dict()
        place_dict["city_id"] = ObjectId(place_data.city_id)
        place_dict["state_id"] = ObjectId(place_data.state_id)
        place_model = PlaceModel(**place_dict)
        place_dict = place_model.dict(by_alias=True, exclude={"id"})
        
        # Insert into database
        result = await collection.insert_one(place_dict)
        
        # Fetch the created place
        created_place = await collection.find_one({"_id": result.inserted_id})
        return PlaceResponse(**created_place)

    async def get_place_by_id(self, place_id: str) -> PlaceResponse:
        """Get place by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(place_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid place ID format"
            )
        
        place = await collection.find_one({"_id": ObjectId(place_id)})
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        return PlaceResponse(**place)

    async def get_places(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search: Optional[str] = None,
        city_id: Optional[str] = None,
        state_id: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PlaceListResponse:
        """Get list of places with pagination and filtering"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Build filter query
        filter_query = {}
        if search:
            filter_query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"city_name": {"$regex": search, "$options": "i"}},
                {"state_name": {"$regex": search, "$options": "i"}}
            ]
        if city_id:
            if not ObjectId.is_valid(city_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid city ID format"
                )
            filter_query["city_id"] = ObjectId(city_id)
        if state_id:
            if not ObjectId.is_valid(state_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state ID format"
                )
            filter_query["state_id"] = ObjectId(state_id)
        if category:
            filter_query["category"] = {"$regex": category, "$options": "i"}
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        # Get total count
        total = await collection.count_documents(filter_query)
        
        # Get places with pagination
        cursor = collection.find(filter_query).skip(skip).limit(limit)
        places = await cursor.to_list(length=limit)
        
        # Convert to response models
        place_responses = [PlaceResponse(**place) for place in places]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = (skip + limit) < total
        has_prev = skip > 0
        
        return PlaceListResponse(
            places=place_responses,
            total=total,
            page=page,
            size=limit,
            has_next=has_next,
            has_prev=has_prev
        )

    async def update_place(self, place_id: str, place_data: PlaceUpdate) -> PlaceResponse:
        """Update place by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(place_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid place ID format"
            )
        
        # Check if place exists
        existing_place = await collection.find_one({"_id": ObjectId(place_id)})
        if not existing_place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        # Validate city_id and state_id if provided
        if place_data.city_id:
            if not ObjectId.is_valid(place_data.city_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid city ID format"
                )
            
            # Check if city exists
            cities_collection = db["cities"]
            city = await cities_collection.find_one({"_id": ObjectId(place_data.city_id)})
            if not city:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="City not found"
                )
        
        if place_data.state_id:
            if not ObjectId.is_valid(place_data.state_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state ID format"
                )
            
            # Check if state exists
            states_collection = db["states"]
            state = await states_collection.find_one({"_id": ObjectId(place_data.state_id)})
            if not state:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="State not found"
                )
        
        # Check if new name conflicts with existing place in same city
        if place_data.name:
            city_id_to_check = ObjectId(place_data.city_id) if place_data.city_id else existing_place["city_id"]
            name_conflict = await collection.find_one({
                "name": place_data.name,
                "city_id": city_id_to_check,
                "_id": {"$ne": ObjectId(place_id)}
            })
            if name_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Place '{place_data.name}' already exists in this city"
                )
        
        # Prepare update data
        update_data = {k: v for k, v in place_data.dict().items() if v is not None}
        if update_data:
            if "city_id" in update_data:
                update_data["city_id"] = ObjectId(update_data["city_id"])
            if "state_id" in update_data:
                update_data["state_id"] = ObjectId(update_data["state_id"])
            update_data["updated_at"] = PlaceModel().updated_at
        
        # Update place
        await collection.update_one(
            {"_id": ObjectId(place_id)},
            {"$set": update_data}
        )
        
        # Return updated place
        updated_place = await collection.find_one({"_id": ObjectId(place_id)})
        return PlaceResponse(**updated_place)

    async def delete_place(self, place_id: str) -> dict:
        """Delete place by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(place_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid place ID format"
            )
        
        # Check if place exists
        existing_place = await collection.find_one({"_id": ObjectId(place_id)})
        if not existing_place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        # Delete place
        await collection.delete_one({"_id": ObjectId(place_id)})
        
        return {"message": "Place deleted successfully"}

    async def get_places_by_city(self, city_id: str) -> List[PlaceResponse]:
        """Get all places by city ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        cursor = collection.find({"city_id": ObjectId(city_id), "is_active": True})
        places = await cursor.to_list(length=None)
        
        return [PlaceResponse(**place) for place in places]

    async def get_places_by_state(self, state_id: str) -> List[PlaceResponse]:
        """Get all places by state ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        cursor = collection.find({"state_id": ObjectId(state_id), "is_active": True})
        places = await cursor.to_list(length=None)
        
        return [PlaceResponse(**place) for place in places]

    async def search_places_nearby(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 10.0,
        limit: int = 20
    ) -> List[PlaceResponse]:
        """Search places within a radius of given coordinates"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # MongoDB geospatial query
        query = {
            "latitude": {"$exists": True, "$ne": None},
            "longitude": {"$exists": True, "$ne": None},
            "is_active": True,
            "$expr": {
                "$lte": [
                    {
                        "$multiply": [
                            6371,  # Earth's radius in km
                            {
                                "$acos": {
                                    "$add": [
                                        {
                                            "$multiply": [
                                                {"$sin": {"$degreesToRadians": "$latitude"}},
                                                {"$sin": {"$degreesToRadians": latitude}}
                                            ]
                                        },
                                        {
                                            "$multiply": [
                                                {"$cos": {"$degreesToRadians": "$latitude"}},
                                                {"$cos": {"$degreesToRadians": latitude}},
                                                {"$cos": {"$degreesToRadians": {"$subtract": ["$longitude", longitude]}}}
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    radius_km
                ]
            }
        }
        
        cursor = collection.find(query).limit(limit)
        places = await cursor.to_list(length=limit)
        
        return [PlaceResponse(**place) for place in places]
