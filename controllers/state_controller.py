from typing import List, Optional, Any
from bson import ObjectId
from fastapi import HTTPException, status
from database import get_database
from models.state import StateModel
from schemas.state import StateCreate, StateUpdate, StateResponse, StateListResponse


class StateController:
    def __init__(self):
        self.collection_name = "states"

    def _convert_object_ids(self, obj: Any) -> Any:
        """Recursively convert ObjectId instances to strings for JSON serialization."""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, list):
            return [self._convert_object_ids(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self._convert_object_ids(value) for key, value in obj.items()}
        return obj

    async def _enrich_locations_with_names(self, db, states: List[dict]) -> List[dict]:
        """Attach country/region names to location items using referenced collections."""
        # Collect unique ids
        country_ids = set()
        region_ids = set()
        for s in states:
            for loc in s.get("location", []) or []:
                country = (loc or {}).get("country") or {}
                region = (loc or {}).get("region") or {}
                if isinstance(country, dict) and country.get("id"):
                    try:
                        country_ids.add(ObjectId(str(country["id"])))
                    except Exception:
                        pass
                if isinstance(region, dict) and region.get("id"):
                    try:
                        region_ids.add(ObjectId(str(region["id"])))
                    except Exception:
                        pass

        # Fetch lookup maps
        countries_map = {}
        regions_map = {}
        if country_ids:
            cursor = db["countries"].find({"_id": {"$in": list(country_ids)}})
            for doc in await cursor.to_list(length=None):
                countries_map[str(doc.get("_id"))] = doc.get("name")
        if region_ids:
            cursor = db["regions"].find({"_id": {"$in": list(region_ids)}})
            for doc in await cursor.to_list(length=None):
                regions_map[str(doc.get("_id"))] = doc.get("name")

        # Inject names
        for s in states:
            for loc in s.get("location", []) or []:
                country = (loc or {}).get("country")
                if isinstance(country, dict) and country.get("id"):
                    cid = str(country["id"]) if not isinstance(country["id"], ObjectId) else str(country["id"])
                    cname = countries_map.get(cid)
                    if cname:
                        country["name"] = cname
                region = (loc or {}).get("region")
                if isinstance(region, dict) and region.get("id"):
                    rid = str(region["id"]) if not isinstance(region["id"], ObjectId) else str(region["id"])
                    rname = regions_map.get(rid)
                    if rname:
                        region["name"] = rname
        return states

    async def _enrich_labels_with_names(self, db, states: List[dict]) -> List[dict]:
        """Attach label names to label items using referenced collections."""
        # Collect unique label ids
        label_ids = set()
        for s in states:
            for label in s.get("labels", []) or []:
                if isinstance(label, dict) and label.get("id"):
                    try:
                        label_ids.add(ObjectId(str(label["id"])))
                    except Exception:
                        pass

        # Fetch lookup map
        labels_map = {}
        if label_ids:
            cursor = db["labels"].find({"_id": {"$in": list(label_ids)}})
            for doc in await cursor.to_list(length=None):
                labels_map[str(doc.get("_id"))] = doc.get("name")

        # Inject names
        for s in states:
            for label in s.get("labels", []) or []:
                if isinstance(label, dict) and label.get("id"):
                    lid = str(label["id"]) if not isinstance(label["id"], ObjectId) else str(label["id"])
                    lname = labels_map.get(lid)
                    if lname:
                        label["name"] = lname
        return states

    async def create_state(self, state_data: StateCreate) -> StateResponse:
        """Create a new state"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Check if state with same code already exists
        existing_state = await collection.find_one({"code": state_data.code})
        if existing_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"State with code '{state_data.code}' already exists"
            )
        
        # Create state model
        state_model = StateModel(**state_data.dict())
        state_dict = state_model.dict(by_alias=True, exclude={"id"})
        
        # Insert into database
        result = await collection.insert_one(state_dict)
        
        # Fetch the created state
        created_state = await collection.find_one({"_id": result.inserted_id})
        created_state = self._convert_object_ids(created_state)
        if created_state and created_state.get("_id") and not created_state.get("id"):
            created_state["id"] = created_state["_id"]
        return StateResponse(**created_state)

    async def get_state_by_id(self, state_id: str) -> StateResponse:
        """Get state by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        state = await collection.find_one({"_id": ObjectId(state_id)})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        state = self._convert_object_ids(state)
        if state and state.get("_id") and not state.get("id"):
            state["id"] = state["_id"]
        return StateResponse(**state)

    async def get_states(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> StateListResponse:
        """Get list of states with pagination and filtering"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Build filter query
        filter_query = {}
        if search:
            filter_query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}}
            ]
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        # Get total count
        total = await collection.count_documents(filter_query)
        
        # Get states with pagination
        cursor = collection.find(filter_query).skip(skip).limit(limit)
        states = await cursor.to_list(length=limit)
        # Enrich names from referenced collections
        states = await self._enrich_locations_with_names(db, states)
        states = await self._enrich_labels_with_names(db, states)
        states = [self._convert_object_ids(s) for s in states]
        for s in states:
            if s.get("_id") and not s.get("id"):
                s["id"] = s["_id"]
        
        # Convert to response models
        state_responses = [StateResponse(**state) for state in states]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = (skip + limit) < total
        has_prev = skip > 0
        
        return StateListResponse(
            states=state_responses,
            total=total,
            page=page,
            size=limit,
            has_next=has_next,
            has_prev=has_prev
        )

    async def update_state(self, state_id: str, state_data: StateUpdate) -> StateResponse:
        """Update state by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        # Check if state exists
        existing_state = await collection.find_one({"_id": ObjectId(state_id)})
        if not existing_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        
        # Check if new code conflicts with existing state
        if state_data.code:
            code_conflict = await collection.find_one({
                "code": state_data.code,
                "_id": {"$ne": ObjectId(state_id)}
            })
            if code_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"State with code '{state_data.code}' already exists"
                )
        
        # Prepare update data
        update_data = {k: v for k, v in state_data.dict().items() if v is not None}
        if update_data:
            update_data["updated_at"] = StateModel().updated_at
        
        # Update state
        await collection.update_one(
            {"_id": ObjectId(state_id)},
            {"$set": update_data}
        )
        
        # Return updated state
        updated_state = await collection.find_one({"_id": ObjectId(state_id)})
        updated_state = self._convert_object_ids(updated_state)
        if updated_state and updated_state.get("_id") and not updated_state.get("id"):
            updated_state["id"] = updated_state["_id"]
        return StateResponse(**updated_state)

    async def delete_state(self, state_id: str) -> dict:
        """Delete state by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        # Check if state exists
        existing_state = await collection.find_one({"_id": ObjectId(state_id)})
        if not existing_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        
        # Check if state has cities
        cities_collection = db["cities"]
        cities_count = await cities_collection.count_documents({"state_id": ObjectId(state_id)})
        if cities_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete state. It has {cities_count} cities associated with it."
            )
        
        # Delete state
        await collection.delete_one({"_id": ObjectId(state_id)})
        
        return {"message": "State deleted successfully"}

    async def get_state_by_code(self, code: str) -> StateResponse:
        """Get state by code"""
        db = await get_database()
        collection = db[self.collection_name]
        
        state = await collection.find_one({"code": code.upper()})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        state = self._convert_object_ids(state)
        if state and state.get("_id") and not state.get("id"):
            state["id"] = state["_id"]
        return StateResponse(**state)

    async def get_all_states(self) -> List[StateResponse]:
        """Get all states from the collection without pagination"""
        db = await get_database()
        collection = db[self.collection_name]
        
        cursor = collection.find({})
        states = await cursor.to_list(length=None)
        states = await self._enrich_locations_with_names(db, states)
        states = await self._enrich_labels_with_names(db, states)
        states = [self._convert_object_ids(s) for s in states]
        for s in states:
            if s.get("_id") and not s.get("id"):
                s["id"] = s["_id"]
        
        return [StateResponse(**state) for state in states]

    async def get_states_page(self, skip: int, limit: int) -> List[StateResponse]:
        """Return a page (array) of states without metadata, for POST /all use case"""
        db = await get_database()
        collection = db[self.collection_name]
        cursor = collection.find({}).skip(skip).limit(limit)
        states = await cursor.to_list(length=limit)
        states = await self._enrich_locations_with_names(db, states)
        states = await self._enrich_labels_with_names(db, states)
        states = [self._convert_object_ids(s) for s in states]
        for s in states:
            if s.get("_id") and not s.get("id"):
                s["id"] = s["_id"]
        return [StateResponse(**state) for state in states]
